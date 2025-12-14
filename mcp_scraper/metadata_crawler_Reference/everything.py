import requests
import os
import json
import re

# 저장 경로
OUTPUT_DIR = "result_json"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "everything_tools.json")

# GitHub 대상 파일
RAW_URL = "https://api.github.com/repos/modelcontextprotocol/servers/contents/src/everything/everything.ts"

# 정규식 패턴
re_name = re.compile(r'name:\s*ToolName\.([A-Z_]+)')
re_desc = re.compile(r'description:\s*"([^"]+)"')

# GitHub Token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# 파일 다운로드
res = requests.get(RAW_URL, headers=HEADERS)
if res.status_code != 200:
    raise Exception("Fail")

raw = res.json()
content = requests.get(raw["download_url"], headers=HEADERS).text

# Handler block 추출
block = re.search(
    r'server\.setRequestHandler\s*\(\s*ListToolsRequestSchema[\s\S]*?return\s*\{\s*tools\s*\};',
    content
)
block_text = block.group(0)

# name/description 추출
re_name = re.compile(r'name:\s*ToolName\.([A-Z_]+)')
re_desc = re.compile(r'description:\s*"([^"]+)"')

names = re_name.findall(block_text)
descs = re_desc.findall(block_text)

if len(names) != len(descs):
    print("name 개수와 description 개수가 일치하지 않습니다. 수동 확인 필요.")

results = []
for i, (name, desc) in enumerate(zip(names, descs), start=1):
    results.append({
        "순서": i,
        "name": name,
        "description": desc
    })

# JSON 저장
os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"총 {len(results)}개의 Tool 추출됨")