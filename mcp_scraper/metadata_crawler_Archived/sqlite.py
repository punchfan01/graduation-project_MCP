import requests
import os
import json
import re


RAW_URL = "https://api.github.com/repos/modelcontextprotocol/servers-archived/contents/src/sqlite/src/mcp_server_sqlite/server.py"


OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "sqlite_tools.json")


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}



res = requests.get(RAW_URL, headers=HEADERS)
raw = res.json()
content = requests.get(raw["download_url"], headers=HEADERS).text


tool_blocks = re.findall(
    r'types\.Tool\s*\(\s*[\s\S]*?\)',   
    content
)


re_name = re.compile(r'name\s*=\s*"([^"]+)"')
re_desc = re.compile(r'description\s*=\s*"([^"]+)"')

results = []
index = 1

for tb in tool_blocks:
    name_match = re_name.search(tb)
    desc_match = re_desc.search(tb)
    if not name_match or not desc_match:
        continue

    name = name_match.group(1)
    description = desc_match.group(1)

    results.append({
        "순서": index,
        "name": name,
        "description": description
    })
    index += 1


os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"{len(results)}개의 SQLite Tool 추출됨")