import requests
import os
import json
import re

OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "firebase_tools.json")

RAW_URL = "https://raw.githubusercontent.com/firebase/firebase-tools/refs/heads/master/src/mcp/README.md"

res = requests.get(RAW_URL)
if res.status_code != 200:
    raise Exception(f"README 수신 실패: {RAW_URL}")
raw = res.text

lines = raw.splitlines()

results = []
index = 1
in_table = False

for line in lines:
    if line.strip().startswith("| Prompt Name"):
        break

    if line.strip().startswith("| Tool Name"):
        in_table = True
        continue

    if in_table and re.match(r"\|\s*-+\s*\|\s*-+\s*\|\s*-+", line):
        continue

    if in_table and line.startswith("|"):
        cols = [col.strip() for col in line.split("|")[1:-1]]
        if len(cols) >= 3:
            name = cols[0]
            description = cols[2]

            results.append({
                "순서": index,
                "name": name,
                "description": description
            })
            index += 1

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

tool_count = len(results)
name_count = sum(1 for x in results if x.get("name"))
description_count = sum(
    1 for x in results if x.get("description") and x["description"].strip() not in ["", "|"]
)

print("\n크롤링 완료")
print(f"Tool 개수: {tool_count}")
print(f"name 개수: {name_count}")
print(f"description 개수: {description_count}")