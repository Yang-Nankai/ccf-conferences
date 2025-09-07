import os
import re
import yaml
import requests

# 远程 YAML URL
YAML_URL = "https://ccfddl.com/conference/allconf.yml"

# 输出目录
output_dir = "conference_htmls"
os.makedirs(output_dir, exist_ok=True)

# CSS 文件
css_content = """
.conference-row {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
    background: #f9fafc;
    padding: 20px;
    border: 1px solid #ebeef5;
    border-radius: 10px;
    margin: 20px auto;
    box-shadow: 0 4px 8px rgba(0, 0, 0, .08);
    max-width: 600px;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
}
.conference-info, .deadline-info { width: 100%; text-align: left; }
.conference-title { font-size: 22px; margin: 0 0 8px 0; color: #2c3e50; line-height: 1.3; }
.conference-title .tag { background: #ecf5ff; border: 1px solid #d9ecff; color: #409eff; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 8px; }
.link { color: #409eff; text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.2s; }
.link:hover { border-color: #409eff; }
.conference-date, .conference-desc { margin: 6px 0; font-size: 14px; color: #606266; }
.conference-tags { margin: 8px 0; }
.note { display: inline-block; color: #e67e22; font-size: 13px; }
.deadline-dates { display: flex; gap: 16px; margin-bottom: 12px; }
.deadline-item { font-size: 14px; font-weight: bold; color: #2c3e50; }
.deadline-text, .website { margin: 6px 0; font-size: 14px; color: #606266; }
"""

# 保存 CSS
css_file = os.path.join(output_dir, "style.css")
with open(css_file, "w", encoding="utf-8") as f:
    f.write(css_content)
print(f"CSS file saved: {css_file}")

# 获取 YAML 数据
res = requests.get(YAML_URL)
res.raise_for_status()
text = res.content.decode('utf-8-sig')
all_confs = yaml.safe_load(text)

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title} {year}</title>
<link rel="stylesheet" href="style.css">
<script src="https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js"></script>
</head>
<body>
<div class="conference-row" id="conference-row">
    <div class="conference-info" id="conference-info">
        Loading conference data...
    </div>
</div>
<script>
function renderCountdown(targetId, deadline) {{
    const el = document.getElementById(targetId);
    function update() {{
        const now = new Date();
        if (!deadline || deadline === 'TBD') return el.textContent = 'TBD';
        const diff = new Date(deadline) - now;
        if (diff <= 0) return el.textContent = 'Passed';
        const days = Math.floor(diff / (1000*60*60*24));
        const hours = Math.floor((diff / (1000*60*60)) % 24);
        const minutes = Math.floor((diff / (1000*60)) % 60);
        const seconds = Math.floor((diff / 1000) % 60);
        el.textContent = `${{days}}d ${{hours}}h ${{minutes}}m ${{seconds}}s`;
    }}
    update();
    setInterval(update, 1000);
}}

(function() {{
    const abstractDeadline = "{abstract_deadline}";
    const submitDeadline = "{submit_deadline}";

    document.getElementById('conference-info').innerHTML = `
        <h3 class="conference-title">
            <a href="https://dblp.uni-trier.de/db/conf/{dblp}" class="link">{title}</a> {year} 
            <span class="tag">CCF {ccf_rank}</span>
        </h3>
        <p class="conference-date">{date} · {place}</p>
        <p class="conference-desc">{description}</p>
        <div class="conference-tags">
            <span class="note"><b>NOTE:</b> abstract deadline on {abstract_deadline}</span>
        </div>
        <div class="deadline-info">
            <div class="deadline-dates">
                <div class="deadline-item"><strong>Abstract Due:</strong> <span id="abstract-countdown">Loading...</span></div>
                <div class="deadline-item"><strong>Submit Due:</strong> <span id="submit-countdown">Loading...</span></div>
            </div>
            <p class="deadline-text">Deadline: {submit_deadline}</p>
            <p class="website">Website: <a href="{link}" class="link">{link}</a></p>
        </div>
    `;

    renderCountdown("abstract-countdown", abstractDeadline);
    renderCountdown("submit-countdown", submitDeadline);
}})();
</script>
</body>
</html>
"""

# 批量生成 HTML
for conf in all_confs:
    for year_info in conf.get("confs", []):
        year = year_info.get("year")
        html_content = HTML_TEMPLATE.format(
            title=conf.get("title", "N/A"),
            dblp=conf.get("dblp", "#"),
            ccf_rank=conf.get("rank", {}).get("ccf", "N/A"),
            year=year,
            date=year_info.get("date", "TBD"),
            place=year_info.get("place", "TBD"),
            description=conf.get("description", ""),
            abstract_deadline=year_info.get("timeline", [{}])[0].get("abstract_deadline", "TBD"),
            submit_deadline=year_info.get("timeline", [{}])[0].get("deadline", "TBD"),
            link=year_info.get("link", "#")
        )

        # 文件名安全化
        raw_name = f"{conf.get('title', 'conf')}_{year}"
        file_name = re.sub(r'[\\/:"*?<>|]+', "_", raw_name) + ".html"
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Generated: {file_path}")

print("All HTML files generated successfully!")
