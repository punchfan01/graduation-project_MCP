import requests
import os
import json
import re

RAW_URL = "https://api.github.com/repos/modelcontextprotocol/servers-archived/contents/src/gitlab/index.ts"

OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "gitlab_tools.json")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


res = requests.get(RAW_URL, headers=HEADERS)
raw = res.json()
content = requests.get(raw["download_url"], headers=HEADERS).text


block_match = re.search(
    r'tools\s*:\s*\[\s*([\s\S]*?)\s*\]',
    content
)

if not block_match:
    raise Exception("배열을 찾지 못했습니다.")

block = block_match.group(1)


re_name = re.compile(r'name\s*:\s*"([^"]+)"')
re_desc = re.compile(r'description\s*:\s*"([^"]+)"')

names = re_name.findall(block)
descs = re_desc.findall(block)

results = []
for idx, (name, desc) in enumerate(zip(names, descs), start=1):
    results.append({
        "순서": idx,
        "name": name,
        "description": desc
    })


os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"{len(results)}개의 Tool 추출됨")