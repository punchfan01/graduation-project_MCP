import requests
import os
import json
import re

RAW_URL = "https://raw.githubusercontent.com/grab/cursor-talk-to-figma-mcp/refs/heads/main/src/talk_to_figma_mcp/server.ts"

OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "figma_tools.json")

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


print(f"tool 개수: {len(results)}")