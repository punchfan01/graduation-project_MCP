import requests
import os
import json
import re

RAW_URL = "https://raw.githubusercontent.com/Klavis-AI/klavis/refs/heads/main/mcp_servers/resend/index.ts"

OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "resend_tools.json")

res = requests.get(RAW_URL)
if res.status_code != 200:
    raise Exception(f"파일 수신 실패: {RAW_URL}")
source = res.text

pattern = re.compile(
    r'server\.tool\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']',
    re.DOTALL
)

matches = pattern.findall(source)

results = []
for idx, (name, description) in enumerate(matches, start=1):
    results.append({
        "순서": idx,
        "name": name,
        "description": description
    })

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

tool_count = len(results)
name_count = sum(1 for x in results if x.get("name") and x["name"].strip())
description_count = sum(1 for x in results if x.get("description") and x["description"].strip())

print(f"Tool 개수: {tool_count}")
print(f"name 개수: {name_count}")
print(f"description 개수: {description_count}")