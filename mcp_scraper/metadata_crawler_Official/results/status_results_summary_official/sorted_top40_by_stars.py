import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

INPUT = r"status_ok_404.json"

OUTPUT = r"top40_by_stars.json"

if not os.path.exists(INPUT):
    raise FileNotFoundError(f"입력 JSON을 찾을 수 없음 → {INPUT}")

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

valid = [d for d in data if d.get("status") == "ok" and d.get("url", "").startswith("https://github.com/")]

def get_repo_info(url):
    owner, repo = url.replace("https://github.com/", "").split("/")[:2]
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=HEADERS)
    if r.status_code != 200:
        return None
    info = r.json()
    return {
        "stars": info.get("stargazers_count", 0),
        "forks": info.get("forks_count", 0),
        "description": info.get("description", None)
    }

results = []

for item in valid:
    url = item["url"]
    info = get_repo_info(url)
    if not info:
        continue
    results.append({
        "name": item["name"],
        "url": url,
        "stars": info["stars"],
        "forks": info["forks"],
        "description": info["description"]
    })

results_sorted = sorted(results, key=lambda x: x["stars"], reverse=True)
top40 = results_sorted[:40]

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(top40, f, ensure_ascii=False, indent=2)

print(f"수집된 정상 repo 수: {len(results)}")
print(f"Top 40 저장 완료 → {OUTPUT}")