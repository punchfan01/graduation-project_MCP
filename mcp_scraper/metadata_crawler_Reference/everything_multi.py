import requests
import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

OWNER = "modelcontextprotocol"
REPO = "servers"
TARGET_PATH = "src/everything/everything.ts"

OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "everything_tools.json")

# 정규식
re_name = re.compile(r'name:\s*ToolName\.([A-Z_]+)')
re_desc = re.compile(r'description:\s*"([^"]+)"')

def list_files_in_path(path):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f"경로 조회 실패 → {url}")
    return res.json()

def fetch_file_raw(download_url):
    r = requests.get(download_url, headers=HEADERS)
    if r.status_code != 200:
        return None
    return r.text



# 크롤링 실행

results = []
index = 1

items = list_files_in_path(TARGET_PATH)

for item in items:
    if item["type"] != "file":
        continue
    if not item["name"].endswith(".ts"):
        continue

    raw = fetch_file_raw(item["download_url"])
    if not raw:
        continue

    name_match = re_name.search(raw)
    desc_match = re_desc.search(raw)

    if not name_match:
        continue  # Tool이 없는 파일은 skip

    name = name_match.group(1)
    description = desc_match.group(1) if desc_match else ""

    results.append({
        "순서": index,
        "name": name,
        "description": description,
    })
    index += 1



# JSON 저장
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"{len(results)}개의 Tool 추출됨")