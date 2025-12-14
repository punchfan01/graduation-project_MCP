import requests
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

OWNER = "ChromeDevTools"
REPO = "chrome-devtools-mcp"
TARGET_PATH = "src/tools"
OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "chromedevtools_tools.json")

results = []
index = 1

def list_files(path):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else []


def fetch_raw(download_url):
    r = requests.get(download_url, headers=HEADERS)
    return r.text if r.status_code == 200 else None

re_block = re.compile(r"defineTool\s*\(\s*\{([\s\S]*?)\}\s*\)", re.MULTILINE)

re_name = re.compile(r"name\s*:\s*(['\"])([^'\"]+)\1")

re_desc = re.compile(r"description\s*:\s*(['\"`])([\s\S]*?)\1")

files = list_files(TARGET_PATH)

name_count = 0
desc_count = 0
tool_count = 0

for item in files:
    if item["type"] != "file":
        continue
    if not item["name"].endswith(".ts"):
        continue

    raw = fetch_raw(item["download_url"])
    if not raw:
        continue

    blocks = re_block.findall(raw)
    if not blocks:
        continue

    for block in blocks:
        name_match = re_name.search(block)
        desc_match = re_desc.search(block)

        if not name_match:
            continue

        name = name_match.group(2)
        description = desc_match.group(2) if desc_match else ""

        results.append({
            "순서": index,
            "name": name,
            "description": description
        })
        index += 1

        tool_count += 1
        name_count += 1
        if description:
            desc_count += 1
os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)


print(f"추출된 Tool 개수: {tool_count}")
print(f"name 추출 개수: {name_count}")
print(f"description 추출 개수: {desc_count}")