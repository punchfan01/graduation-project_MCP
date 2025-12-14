import requests
import re
import base64
import json
import os
from dotenv import load_dotenv


load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

RAW_URL = "https://raw.githubusercontent.com/modelcontextprotocol/servers/refs/heads/main/README.md"
OUTPUT = "results/official_integrations_summary.json"

os.makedirs("results", exist_ok=True)

readme = requests.get(RAW_URL).text


pattern = r"###.*official.*integration[s]?.*?(\n[\s\S]*?)###.*community\s+servers"
match = re.search(pattern, readme, re.IGNORECASE)
if not match:
    raise RuntimeError("Official Integrations 섹션을 찾지 못했습니다.")
section = match.group(1)


lines = [ln.strip() for ln in section.split("\n") if ln.strip().startswith("- ")]



first_link_pattern = re.compile(r"- .*?\*\*\[([^\]]+)\]\((https?://[^\)]+)\)")

targets = []
for ln in lines:
    m = first_link_pattern.search(ln)
    if m:
        name, url = m.group(1).strip(), m.group(2).strip()
        targets.append({"name": name, "url": url})
    else:
        targets.append({"name": None, "url": None})



def find_readme_title(owner, repo):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/readme", headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        if "content" in data:
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return extract_title(content)
        else:
            return None

    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents", headers=HEADERS)
    if r.status_code == 200:
        for f in r.json():
            if re.match(r"readme\..*", f["name"], re.IGNORECASE):
                return fetch_readme(owner, repo, f["path"])

    for folder in ["docs", "server", "packages", "src"]:
        r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{folder}", headers=HEADERS)
        if r.status_code == 200:
            for f in r.json():
                if re.match(r"readme\..*", f["name"], re.IGNORECASE):
                    return fetch_readme(owner, repo, f"{folder}/{f['name']}")

    return None


def fetch_readme(owner, repo, path):
    rr = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=HEADERS)
    if rr.status_code == 200 and "content" in rr.json():
        return extract_title(base64.b64decode(rr.json()["content"]).decode("utf-8", errors="replace"))
    return None

def extract_title(content):
    for ln in content.split("\n"):
        if ln.startswith("#"):
            return ln.lstrip("#").strip()
    return None

results = []
count_ok = count_error = count_non = 0

for t in targets:
    name, url = t["name"], t["url"]

    if not url:
        results.append({"name": name, "url": None, "status": "no_link", "title": None})
        count_non += 1
        continue

    if not url.startswith("https://github.com/"):
        results.append({"name": name, "url": url, "status": "non_github", "title": None})
        count_non += 1
        continue

    owner, repo = url.replace("https://github.com/", "").split("/")[:2]
    title = find_readme_title(owner, repo)

    if title:
        results.append({"name": name, "url": url, "status": "ok", "title": title})
        count_ok += 1
    else:
        results.append({"name": name, "url": url, "status": "github_error", "title": None})
        count_error += 1


with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

total = len(results)

print(f"정상 수집 (ok): {count_ok}")
print(f"GitHub 오류 (github_error): {count_error}")
print(f"GitHub 외 링크/없음 (non_github 포함): {count_non}")
print(f"총: {total}")