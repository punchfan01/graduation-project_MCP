import requests
import os
import json
import re


RAW_URL = "https://api.github.com/repos/modelcontextprotocol/servers-archived/contents/src/google-maps/index.ts"


OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "google_maps_tools.json")


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


res = requests.get(RAW_URL, headers=HEADERS)
raw = res.json()
content = requests.get(raw["download_url"], headers=HEADERS).text


re_name = re.compile(r'name\s*:\s*"([^"]+)"')
re_desc = re.compile(r'description\s*:\s*"([^"]+)"')

names = re_name.findall(content)
descs = re_desc.findall(content)

if len(names) != len(descs):
    print(f"name={len(names)}, description={len(descs)}. 개수 불일치.")


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