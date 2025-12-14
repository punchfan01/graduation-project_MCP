import requests
import os
import json
import re


API_DIR_URL = "https://api.github.com/repos/brave/brave-search-mcp-server/contents/src/tools"


OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "bravesearch_tools.json")


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


def fetch(url):
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f"Fail: {url}")
    return res.json()



items = fetch(API_DIR_URL)


index_files = [
    item for item in items
    if item["type"] == "dir"  
] + [
    item for item in items
    if item["type"] == "file" and item["name"] == "index.ts"  
]

target_urls = []


for item in items:
    if item["type"] == "dir":
        sub = fetch(item["url"])
        for f in sub:
            if f["type"] == "file" and f["name"] == "index.ts":
                target_urls.append(f["download_url"])


for item in items:
    if item["type"] == "file" and item["name"] == "index.ts":
        target_urls.append(item["download_url"])


re_name = re.compile(r'export const name\s*=\s*[\'"]([^\'"]+)[\'"]')
re_desc = re.compile(r'export const description\s*=\s*`([\s\S]*?)`')



results = []
index = 1

for url in target_urls:
    raw = requests.get(url, headers=HEADERS).text

    name_match = re_name.search(raw)
    desc_match = re_desc.search(raw)

    if not name_match or not desc_match:
        continue

    name = name_match.group(1)
    description = desc_match.group(1).strip()

    results.append({
        "순서": index,
        "name": name,
        "description": description
    })
    index += 1



os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"index.ts {len(results)}개 파일에서 tool 정의 수집 완료")