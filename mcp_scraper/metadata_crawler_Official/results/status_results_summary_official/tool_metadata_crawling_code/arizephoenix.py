import requests
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

OWNER = "Arize-ai"
REPO = "phoenix"
TARGET_PATH = "js/packages/phoenix-mcp/src"
OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "phoenix_tools.json")

re_server_tool = re.compile(r"server\.tool\s*\(", re.MULTILINE)
re_first_arg = re.compile(r'^\s*"([^"]+)"', re.MULTILINE)  # 첫 번째 인수 literal name
re_second_string = re.compile(r'^\s*"([^"]+)"', re.MULTILINE)  # 문자열 description
re_second_var = re.compile(r'^\s*([A-Za-z0-9_]+)\s*[,)]', re.MULTILINE)  # 변수 description
re_template_vars = re.compile(r'const\s+([A-Za-z0-9_]+)\s*=\s*`([^`]+)`', re.DOTALL)

def list_files(path):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    return requests.get(url, headers=HEADERS).json()

def fetch_raw(download_url):
    r = requests.get(download_url, headers=HEADERS)
    return r.text if r.status_code == 200 else None

files = list_files(TARGET_PATH)
results = []
index = 1

for f in files:
    if f["type"] != "file" or not f["name"].endswith(".ts"):
        continue

    raw = fetch_raw(f["download_url"])
    if not raw:
        continue

    var_templates = {m.group(1): m.group(2).strip() for m in re_template_vars.finditer(raw)}

    blocks = raw.split("server.tool(")
    if len(blocks) <= 1:
        continue

    for block in blocks[1:]:
        
        name_match = re_first_arg.search(block)
        if not name_match:
            continue
        name = name_match.group(1).strip()

        desc = ""
        desc_literal = re_second_string.search(block)
        desc_var = re_second_var.search(block)

        if desc_literal and desc_literal.group(1).strip() != name:
            desc = desc_literal.group(1).strip()
        elif desc_var:
            var_name = desc_var.group(1).strip()
            desc = var_templates.get(var_name, var_name)

        results.append({
            "순서": index,
            "name": name,
            "description": desc,
        })
        index += 1

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

tool_count = len(results)
name_count = sum(1 for x in results if x.get("name"))
description_count = sum(1 for x in results if x.get("description") and x["description"].strip() not in ["", "|"])

print("\n크롤링 완료")
print(f"Tool 개수: {tool_count}")
print(f"name 개수: {name_count}")
print(f"description 개수: {description_count}")