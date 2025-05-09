import parser
import sys
import json

import csv

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
        for sub in slot["SUB"].values():
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

    print(f"攻撃力: {base_attack} -> {base_attack * attack:.2f}")
    print(f"クリティカル: {base_critical} -> {critical:.2f}")
    print(f"クリティカルダメージ: {base_damage} -> {damage:.2f}")
    print(f"ダメージアップ: {base_damage_up} -> {damage_up:.2f}")

    print(f"期待値:" 
          f"{1.0 * (1 + base_critical * base_damage) * (1 + base_damage_up):.2f}"
          " -> "
          f"{attack * (1 + critical * damage) * (1 + damage_up):.2f}"
          " : "
          f"{(attack * (1 + critical * damage) * (1 + damage_up)) / (1.0 * (1 + base_critical * base_damage) * (1 + base_damage_up)):.2f}"
          "倍"
          )