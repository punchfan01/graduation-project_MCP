import json

FILE = r"mcptoolboxfordatabases_tools.json"

with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

tool_count = len(data)

name_count = sum(1 for item in data if item.get("name") and item["name"].strip())

# description이 비어있거나, 공백이거나, '|' 같은 placeholder면 제외
def valid_description(desc):
    if not desc:
        return False
    d = desc.strip()
    if d == "" or d == "|":
        return False
    return True

description_count = sum(1 for item in data if valid_description(item.get("description")))

print("📌 JSON 분석 결과")
print(f"🛠 Tool 개수: {tool_count}")
print(f"🏷 name 개수: {name_count}")
print(f"📝 description 개수: {description_count}")
