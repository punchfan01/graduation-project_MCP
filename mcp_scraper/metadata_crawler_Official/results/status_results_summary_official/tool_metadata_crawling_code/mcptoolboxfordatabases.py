import requests
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

OWNER = "googleapis"
REPO = "genai-toolbox"
ROOT_PATH = "docs/en/resources/tools"
OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "mcptoolboxfordatabases_tools.json")

results = []
index = 1

def list_contents(path):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else []

def fetch_raw(download_url):
    r = requests.get(download_url, headers=HEADERS)
    return r.text if r.status_code == 200 else None

re_yaml_block = re.compile(r"```yaml([\s\S]*?)```", re.MULTILINE)

re_tool_name = re.compile(r"^\s{2}([a-zA-Z0-9_\-]+)\s*:\s*$", re.MULTILINE)

re_description = re.compile(r"description\s*:\s*(.+)")

def parse_yaml_block(block):
    tools_section = block.split("tools:", 1)
    if len(tools_section) < 2:
        return []

    section = tools_section[1]
    names = re_tool_name.findall(section)
    descriptions = re_description.findall(section)

    pairs = []
    for idx, name in enumerate(names):
        desc = descriptions[idx] if idx < len(descriptions) else ""
        pairs.append((name, desc.strip()))
    return pairs

folders = list_contents(ROOT_PATH)

for folder in folders:
    if folder["type"] != "dir":
        continue

    subfiles = list_contents(folder["path"])
    for item in subfiles:
        if item["type"] != "file":
            continue
        if not item["name"].endswith(".md"):
            continue

        raw = fetch_raw(item["download_url"])
        if not raw:
            continue

        yaml_blocks = re_yaml_block.findall(raw)
        if not yaml_blocks:
            continue

        for block in yaml_blocks:
            pairs = parse_yaml_block(block)
            for name, description in pairs:
                results.append({
                    "순서": index,
                    "name": name,
                    "description": description
                })
                index += 1

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"총 Tool 개수: {len(results)}")