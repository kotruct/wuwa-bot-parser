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
                    result[key] = value
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

    attack = data["攻撃力"]
    critical = data["クリティカル"]
    damage = data["クリティカルダメージ"]
    damage_up = data["クリティカルダメージアップ"]

    for slot in json_data["slots"]:
        if slot["MAIN"]["name"] == "攻撃力":
            attack += json_data["slots"][slot]["MAIN"]["value"]
        elif slot["MAIN"]["name"] == "クリティカル":
            critical += json_data["slots"][slot]["MAIN"]["value"]
        elif slot["MAIN"]["name"] == "クリティカルダメージ":
            damage += json_data["slots"][slot]["MAIN"]["value"]
