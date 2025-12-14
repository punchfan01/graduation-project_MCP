import json

files_and_categories = [
    ("repo_name_des_reference.json", "reference"),
    ("repo_name_des_archived.json", "archived"),
    ("repo_name_des_official.json", "official"),
    ("repo_name_des_community.json", "community"),
]

merged = []
index = 1

for filename, category in files_and_categories:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data:
        entry_ordered = {
            "index": index,
            "category": category,
            **entry
        }
        merged.append(entry_ordered)
        index += 1

output_file = "repo_name_des_merged.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)
    
print(f"총 {len(merged)}개의 레코드가 저장되었으며 index + category 필드가 추가되었습니다.")