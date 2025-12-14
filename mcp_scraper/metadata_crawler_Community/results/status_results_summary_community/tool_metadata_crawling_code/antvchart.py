import requests
import os
import json
import re

BASE_RAW = "https://raw.githubusercontent.com/antvis/mcp-server-chart/refs/heads/main/src/charts"
OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "chart_tools.json")

list_url = "https://api.github.com/repos/antvis/mcp-server-chart/contents/src/charts"
resp = requests.get(list_url)
if resp.status_code != 200:
    raise Exception("폴더 목록을 가져오지 못했습니다.")
files = resp.json()

ts_files = [f["name"] for f in files if f["name"].endswith(".ts")]

results = []
index = 1


for file in ts_files:
    raw_url = f"{BASE_RAW}/{file}"
    res = requests.get(raw_url)
    if res.status_code != 200:
        print(f"파일 다운로드 실패 → {file}")
        continue

    src = res.text

    pattern = re.compile(
        r'const\s+tool\s*=\s*\{\s*[^{}]*?name\s*:\s*["\']([^"\']+)["\']\s*,\s*description\s*:\s*(?:`([^`]*)`|["\']([^"\']+)["\'])',
        re.DOTALL
    )

    matches = pattern.findall(src)
    for m in matches:
        name = m[0]
        desc = m[1] if m[1] else m[2] 
        results.append({
            "순서": index,
            "파일명": file,
            "name": name,
            "description": desc.strip()
        })
        index += 1

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)


tool_count = len(results)
name_count = sum(1 for x in results if x.get("name") and x["name"].strip())
description_count = sum(1 for x in results if x.get("description") and x["description"].strip())

print(f"Tool 개수: {tool_count}")
print(f"name 개수: {name_count}")
print(f"description 개수: {description_count}")