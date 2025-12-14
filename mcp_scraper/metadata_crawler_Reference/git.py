import requests
import os
import json
import re

OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "git_tools.json")

RAW_URL = "https://api.github.com/repos/modelcontextprotocol/servers/contents/src/git/src/mcp_server_git/server.py"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

res = requests.get(RAW_URL, headers=HEADERS)
raw = res.json()
content = requests.get(raw["download_url"], headers=HEADERS).text

block_match = re.search(
    r'@server\.list_tools\(\)[\s\S]*?return\s*\[\s*([\s\S]*?)\s*\]',
    content
)

if not block_match:
    raise Exception("Fail")

block = block_match.group(1)

re_name = re.compile(r'name\s*=\s*GitTools\.([A-Z_]+)')
re_desc = re.compile(r'description\s*=\s*"([^"]+)"')

names = re_name.findall(block)
descs = re_desc.findall(block)

if len(names) != len(descs):
    print(f"이름 {len(names)}, 설명 {len(descs)}. 개수 불일치 가능.")

results = []
for idx, (name, description) in enumerate(zip(names, descs), start=1):
    results.append({
        "순서": idx,
        "name": name,
        "description": description
    })

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"{len(results)}개의 Tool 추출 성공")