"""Task 3 - Step 2: build the interactive dashboard from the template and the data.

Reads : dashboard_template.html, outputs/dashboard_data.json
Writes: dashboard.html          (standalone page for the GitHub repo; open it in any browser, needs internet for Chart.js)
        dashboard_artifact.html (same page without the document wrapper, for publishing as a hosted artifact)
Run   : python 02_build_dashboard.py
"""
from pathlib import Path

BASE = Path(__file__).parent
tpl = (BASE / "dashboard_template.html").read_text(encoding="utf-8")
data = (BASE / "outputs" / "dashboard_data.json").read_text(encoding="utf-8")
assert "__DATA__" in tpl
page = tpl.replace("__DATA__", data)

(BASE / "dashboard_artifact.html").write_text(page, encoding="utf-8")
wrapped = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1">\n</head>\n<body>\n' + page + "\n</body>\n</html>\n")
(BASE / "dashboard.html").write_text(wrapped, encoding="utf-8")
print("dashboard.html", round(len(wrapped) / 1024, 1), "kB")
