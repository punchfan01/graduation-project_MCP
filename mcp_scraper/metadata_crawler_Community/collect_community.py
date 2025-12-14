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
os.makedirs("results", exist_ok=True)

main_readme = requests.get(RAW_URL).text

pattern = r"###.*community servers\b([\s\S]*?)##"
match = re.search(pattern, main_readme, re.IGNORECASE)

if not match:
    raise RuntimeError("Community Servers 섹션을 찾지 못했습니다. README 구조가 변경된 것 같습니다.")

section = match.group(1)

lines = [ln.strip() for ln in section.split("\n") if ln.strip().startswith("- ")]

first_link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

targets = []
for ln in lines:
    m = first_link_pattern.search(ln)
    if m:
        targets.append({"name": m.group(1).strip(), "url": m.group(2).strip()})
    else:
        targets.append({"name": None, "url": None})


def normalize_github_repo_url(url):
    tail = url.replace("https://github.com/", "")
    parts = tail.split("/")
    if len(parts) < 2:  
        return None
    return parts[0], parts[1]

def extract_title(text):
    for line in text.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return None

def fetch_readme_title(owner, repo, path):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=HEADERS)
    if r.status_code == 200 and isinstance(r.json(), dict) and "content" in r.json():
        content = base64.b64decode(r.json()["content"]).decode("utf-8", errors="replace")
        return extract_title(content)
    return None

def get_title_from_repo(url):
    normalized = normalize_github_repo_url(url)
    if normalized is None:
        return None, False  
    owner, repo = normalized

    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents", headers=HEADERS)
    if r.status_code == 200 and isinstance(r.json(), list):
        for f in r.json():
            if re.match(r"readme\..*", f.get("name", ""), re.IGNORECASE):
                return fetch_readme_title(owner, repo, f["path"]), True

    folders = ["docs", "server", "packages", "src"]
    for folder in folders:
        rr = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{folder}", headers=HEADERS)
        if rr.status_code == 200 and isinstance(rr.json(), list):
            for f in rr.json():
                if re.match(r"readme\..*", f.get("name", ""), re.IGNORECASE):
                    return fetch_readme_title(owner, repo, f"{folder}/{f['name']}"), True

    return None, True 

results = []
ok = github_error = non_github = 0
total = len(targets)

for idx, t in enumerate(targets, start=1):
    name, url = t["name"], t["url"]

    if not url:
        results.append({"name": name, "url": None, "status": "no_link", "title": None})
        non_github += 1
        continue

    if not url.startswith("https://github.com/"):
        results.append({"name": name, "url": url, "status": "non_github", "title": None})
        non_github += 1
        continue

    title, valid = get_title_from_repo(url)
    if valid and title:
        results.append({"name": name, "url": url, "status": "ok", "title": title})
        ok += 1
    else:
        results.append({"name": name, "url": url, "status": "github_error", "title": None})
        github_error += 1

summary_path = "results/community_servers_summary.json"
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

status_dir = "results/status_results_summary_community"
os.makedirs(status_dir, exist_ok=True)
grouped = {"ok": [], "github_error": [], "non_github": []}

for r in results:
    grouped[r["status"]].append(r)

for status, items in grouped.items():
    out = os.path.join(status_dir, f"status_{status}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

print(f"GitHub 성공: {ok}")
print(f"GitHub 오류: {github_error}")
print(f"GitHub 외 링크: {non_github}")