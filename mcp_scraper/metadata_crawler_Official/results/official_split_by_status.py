import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


input_path = os.path.join(BASE_DIR, "official_integrations_summary.json")

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)


output_dir = os.path.join(BASE_DIR, "status_results_summary_official")
os.makedirs(output_dir, exist_ok=True)

grouped = {"ok": [], "github_error": [], "non_github": []}

for item in data:
    status = item.get("status")
    if status in grouped:
        grouped[status].append(item)
    else:
        print("Unknown status found:", status)

for status, items in grouped.items():
    filename = f"status_{status}.json"
    out_path = os.path.join(output_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"{status}: {len(items)}개 저장 → {out_path}")

print("\nstatus별 파일 분리가 끝났습니다.")