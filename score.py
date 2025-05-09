import parser
import sys
import json

import csv
from tabulate  import tabulate

def csv_to_dict(file_path):
    result = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:  # 2カラム以上ある場合のみ処理
                    key, value = row[0], row[1]
                    if "%" in value:
                        value = value.replace("%", "")
                        result[key] = float(value) / 100
                    else:
                        result[key] = float(value)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    return result


if __name__ == "__main__":
    url = sys.argv[1]

    json_data = parser.generate_json(url)

    name = json_data["name"]
    csv_file = f"data/{name}.csv"  # CSVファイルのパス
    data = csv_to_dict(csv_file)
    # print(json.dumps(data, ensure_ascii=False, indent=4))
    with open(f"data/{name}.txt", "r", encoding="utf-8") as file:
            damage_type_list = [line.strip() for line in file if line.strip()]

    attack = 1.0
    base_attack = data["攻撃力"]
    critical = data["クリティカル"]
    base_critical = critical
    damage = data["クリティカルダメージ"]
    base_damage = damage
    damage_up = data["ダメージアップ"]
    base_damage_up = damage_up

    combined_status = []

    for slot in json_data["slots"]:
        # MAINステータスを追加
        combined_status.append({
            "name": slot["MAIN"]["name"],
            "value": slot["MAIN"]["value"]
        })
        # SUBステータスを追加
        for sub in slot["SUB"]:
            combined_status.append({
                "name": sub["name"],
                "value": sub["value"]
            })

    # print(combined_status)

    for status in combined_status:
        if "%" in status["value"]:
            status["value"] = status["value"].replace("%", "")
            status["value"] = float(status["value"]) / 100
        else:
            status["value"] = float(status["value"]) / base_attack

        if "攻撃力" in status["name"]:
            attack += status["value"]
        elif "クリティカルダメージ" in status["name"]:
            damage += status["value"]
        elif "クリティカル" in status["name"]:
            critical += status["value"]
        # elif damage_list in slot["MAIN"]["name"]:
        elif any(damage_type in status["name"] for damage_type in damage_type_list):
            damage_up += status["value"]


    headers = ["ステータス", "基準値", "最終値", "倍率"]
    table = []
    table.append([f'攻撃力', f"{base_attack:.1f}", f"{base_attack * attack:.1f}", f"{attack:.2f}倍"])
    table.append([f'クリティカル', f"{base_critical:.3f}", f"{critical:.3f}", f""])
    table.append([f'クリティカルダメージ', f"{base_damage:.3f}", f"{damage:.3f}", f""])
    table.append([f'クリティカル効果', f"{1 - base_critical + base_critical * base_damage:.3f}", f"{1 - critical + critical * damage:.3f}", f"{(1 - critical + critical * damage) / (1 - base_critical + base_critical * base_damage):.2f}倍"])
    table.append([f'ダメージアップ', f"{base_damage_up:.3f}", f"{damage_up:.3f}", f"{(1+damage_up) / (1+base_damage_up):.2f}倍"])
    table.append([f'期待値', 
                  f"{1.0 * (1 - base_critical + base_critical * base_damage) * (1 + base_damage_up):.3f}", 
                  f"{attack * (1 - critical + critical * damage) * (1 + damage_up):.3f}", 
                  f"{(attack * (1 - critical + critical * damage) * (1 + damage_up)) / (1.0 * (1 - base_critical + base_critical * base_damage) * (1 + base_damage_up)):.2f}倍"
                  ])

    print(tabulate(table, headers=headers, tablefmt="grid", stralign="center", maxcolwidths=[20, 10, 10, 10]))