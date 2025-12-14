import requests
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

OWNER = "firecrawl"
REPO = "firecrawl-mcp-server"
FILE_PATH = "src/index.ts"
OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "firecrawl_tools.json")

re_addtool_blocks = re.compile(r"server\.addTool\s*\(\s*{(.*?)}\s*\)", re.DOTALL)
re_name = re.compile(r"name\s*:\s*['\"]([^'\"]+)['\"]")
re_description = re.compile(r"description\s*:\s*`([^`]+)`", re.DOTALL)

def fetch_file(path):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f"파일 조회 실패 → {url}")
    return res.json()

def fetch_raw(download_url):
    r = requests.get(download_url, headers=HEADERS)
    return r.text if r.status_code == 200 else None

file_meta = fetch_file(FILE_PATH)
raw = fetch_raw(file_meta["download_url"])

results = []
index = 1

blocks = re_addtool_blocks.findall(raw)
for block in blocks:
    name_match = re_name.search(block)
    desc_match = re_description.search(block)

    if not name_match:
        continue

    name = name_match.group(1).strip()
    description = desc_match.group(1).strip() if desc_match else ""

    results.append({
        "순서": index,
        "name": name,
        "description": description,
    })
    index += 1

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

tool_count = len(results)
name_count = sum(1 for x in results if x.get("name"))
description_count = sum(1 for x in results if x.get("description") and x["description"].strip() not in ["", "|"])

print("\n크롤링 완료")
print(f"Tool 개수: {tool_count}")
print(f"name 개수: {name_count}")
print(f"description 개수: {description_count}")