import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

OWNER = "github"
REPO = "github-mcp-server"
START_PATH = "pkg/github/__toolsnaps__"
OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "github_tools.json")

results = []
index = 1

def list_contents(path):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print(f"경로 조회 실패: {url}")
        return []
    return res.json()

def fetch_json(download_url):
    r = requests.get(download_url, headers=HEADERS)
    if r.status_code != 200:
        return None
    try:
        return json.loads(r.text)
    except json.JSONDecodeError:
        return None

def scan_folder(path):
    global index
    items = list_contents(path)

    for item in items:
        item_type = item.get("type")
        item_name = item.get("name")

        if item_type == "dir":
            scan_folder(item["path"])
            continue

        if not (item_type == "file" and (item_name.endswith(".snap") or item_name.endswith(".json"))):
            continue

        data = fetch_json(item["download_url"])
        if not data:
            continue

        name = data.get("name", "")
        description = data.get("description", "") or ""

        results.append({
            "순서": index,
            "name": name,
            "description": description
        })
        index += 1

scan_folder(START_PATH)

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"{len(results)}개의 Tool 추출됨")