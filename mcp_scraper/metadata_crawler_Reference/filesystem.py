import requests
import os
import json
import re

# 저장 경로
OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "filesystem_tools.json")

# GitHub 대상 파일
RAW_URL = "https://api.github.com/repos/modelcontextprotocol/servers/contents/src/filesystem/index.ts"

# GitHub Token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# 다운로드
res = requests.get(RAW_URL, headers=HEADERS)
raw = res.json()
content = requests.get(raw["download_url"], headers=HEADERS).text

blocks = re.findall(r'server\.registerTool\s*\([\s\S]*?\n\s*\)', content)

re_name = re.compile(r'server\.registerTool\s*\(\s*"([^"]+)"')
re_desc = re.compile(r'description:\s*((?:"[^"]*"\s*\+\s*)*"[^"]*")')

results = []
index = 1

for b in blocks:
    name_match = re_name.search(b)
    desc_match = re_desc.search(b)
    if not name_match or not desc_match:
        continue

    name = name_match.group(1)

    description_raw = desc_match.group(1)
    parts = re.findall(r'"([^"]*)"', description_raw)
    description = "".join(parts).strip()

    results.append({
        "순서": index,
        "name": name,
        "description": description
    })
    index += 1

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"{len(results)}개의 Tool 추출됨")