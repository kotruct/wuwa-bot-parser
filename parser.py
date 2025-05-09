from PIL import Image
import cv2
import numpy as np
import re
import sys
import difflib
import os
import json
import uuid

import requests
from io import BytesIO
from tabulate  import tabulate

# 画像読み込み

# # グレースケールに変換してOCRしやすくする
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# gray = cv2.GaussianBlur(gray, (3, 3), 0)
# gray = cv2.addWeighted(gray, 1.5, gray, 0, -20)  # シャープ化
# _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# # Pillowに変換してOCR
# pil_img = Image.fromarray(thresh)
# custom_config = r'--oem 1 --psm 6'
# text = pytesseract.image_to_string(pil_img, lang='jpn', config=custom_config)
# # text = pytesseract.image_to_string(pil_img, lang='jpn')  # 日本語認識

# print(text)

# サブステータスらしき行を正規表現で抽出
#pattern = re.compile(r"([\wぁ-んァ-ン一-龥]+)[\s:：\-]*([\d\.]+)%?")
#matches = pattern.findall(text)

#for stat, value in matches:
#print(f"{stat.strip()}: {value.strip()}")

def region_of_interest(img, field, x1, y1, x2, y2):
    roi = img[y1:y2, x1:x2]
    roi = cv2.resize(roi, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(f"debug/{field}.jpeg", roi)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.addWeighted(gray, 1.5, gray, 0, -20)  # シャープ化
    cv2.imwrite(f"debug/{field}-gray.jpeg", gray)

    return gray

    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(f"debug/{field}-thresh.jpeg", thresh)

    return thresh

def ocr_pytesseract(img, custom_config, lang=None):
    import pytesseract
    if os.name == 'nt':
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if lang is None:
        text = pytesseract.image_to_string(img, config=custom_config).strip()
    else:
    # if "ダメージアップ" in custom_config or "カルロッタ" in custom_config:
        if "HP" == pytesseract.image_to_string(img, config="--oem 1 --psm 7").strip():
            text = "HP"
        else:
            text = pytesseract.image_to_string(img, lang='jpn', config=custom_config).strip()
    return text

def ocr_easyocr(img):  
    import easyocr
    import logging
    logging.getLogger('easyocr').setLevel(logging.ERROR)
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="torch")

    reader = easyocr.Reader(['ja'], gpu=False)
    result = reader.readtext(img, detail=0, paragraph=True)
    # print(result)
    text = ' '.join(result).strip()
    return text

def extract_cost(img):
    # キャリブレーション実施
    upper = 678
    lower = 696
    slotN_left = [338, 710, 1084, 1460, 1835]
    width = 17    

    regions = [(f"cost{i}", slotN_left[i-1], upper, slotN_left[i-1]+width, lower) for i in range(1, 6)]

    ret = {}

    for (field, x1, y1, x2, y2) in regions:
        numpy_img = region_of_interest(img, field, x1, y1, x2, y2)

        custom_config = r'-c tessedit_char_whitelist=134 --oem 1 --psm 7'
        pil_img = Image.fromarray(numpy_img)
        tesseract_text = ocr_pytesseract(pil_img, custom_config)
        # print(f"{field}.tesseract_text : {tesseract_text}")
        ret[field] = tesseract_text

        if tesseract_text == "":
            easyocr_text = ocr_easyocr(numpy_img)
            # print(f"{field}.easyocr_text : {easyocr_text}")
            ret[field] = easyocr_text
    
    return ret

def extract_status_name(img):
    # キャリブレーション実施
    main_upper = 724
    main_lower = 745
    slotN_main_right = [373, 751, 1121, 1496, 1869]
    main_width = 159
    slotN_sub_left = [61, 441, 815, 1190, 1564]
    sub_width = 207
    sub_upper = [884, 918, 953, 986, 1021]
    sub_height = 23


    main_regions = [(f"main-name{i}", slotN_main_right[i-1]-main_width, main_upper, slotN_main_right[i-1], main_lower) for i in range(1, 6)]
    sub_regions = [(f"sub-name{i}-{j}", slotN_sub_left[i-1], sub_upper[j-1], slotN_sub_left[i-1]+sub_width, sub_upper[j-1]+sub_height) for i in range(1, 6) for j in range(1, 6)]

    ret = {}

    for (field, x1, y1, x2, y2) in main_regions + sub_regions:
        numpy_img = region_of_interest(img, field, x1, y1, x2, y2)
        
        # なぜかいったん書き出してから再読み込みすると認識精度が上がる 
        # pngだとダメなのでjpegで保存が効いている？
        tmp_filename = f"tmp_{uuid.uuid4().hex}.jpeg"
        cv2.imwrite(tmp_filename, numpy_img)
        numpy_img = cv2.imread(tmp_filename)
        os.remove(tmp_filename)

        pil_img = Image.fromarray(numpy_img)        
        with open("data/status_names.txt", "r", encoding="utf-8") as file:
            candidates = [line.strip() for line in file if line.strip()]
        whitelist = "クリティカルダメージアップ重撃通常攻撃防御共鳴効率解放スキル凝縮焦熱電導気動回折消滅"
        # whitelist = ''.join(sorted(set(whitelist)))
        # whitelist = ''.join(set(whitelist))

        # candidatesを結合して重複を削除しても動かない　
        # 上の例でもsetしてjoinすると動かなくなる　sortは関係なさそう

        # whitelist = ''.join(sorted(set(''.join(candidates))))
        # remove_str = "HP力"
        # whitelist = ''.join([c for c in whitelist if c not in remove_str])
        # print(whitelist)
        
        custom_config = fr'-c tessedit_char_whitelist={whitelist} --oem 1 --psm 7'
        
        # custom_config = r'-c tessedit_char_whitelist=クリティカルダメージアップ重撃通常攻撃防御共鳴効率解放スキル凝縮焦熱電導気動回折消滅 --oem 1 --psm 7'
        tesseract_text = ocr_pytesseract(pil_img, custom_config, lang='jpn')

        # print(f"{field}.tesseract_text : {tesseract_text}")

        closest = difflib.get_close_matches(tesseract_text, candidates, n=1, cutoff=0.55) # cutoffを上げるとマッチしない
        # print(f"{field}.tesseract_text : {closest[0]}")
        ret[field] = closest[0] 
        
        # easyocr_text = ocr_easyocr(numpy_img)
        # # print(f"{field}.easyocr_text : {easyocr_text}")
        # closest = difflib.get_close_matches(easyocr_text, candidates, n=1)
        # print(f"{field}.easyocr_text : {closest[0] if closest else easyocr_text}")

    return ret

def extract_status_value(img):
    # キャリブレーション実施
    main_upper = 756
    main_lower = 781
    slotN_main_right = [371, 746, 1119, 1494, 1870]
    main_width = 58
    subN_upper = [884, 918, 953, 986, 1021]
    sub_height = 23
    slotN_sub_left = [315, 690, 1063, 1438, 1814]
    sub_width = 61

    main_regions = [(f"main-value{i}", slotN_main_right[i-1]-main_width, main_upper, slotN_main_right[i-1], main_lower) for i in range(1, 6)]
    sub_regions = [(f"sub-value{i}-{j}", slotN_sub_left[i-1], subN_upper[j-1], slotN_sub_left[i-1]+sub_width, subN_upper[j-1]+sub_height) for i in range(1, 6) for j in range(1, 6)]


    ret = {}

    for (field, x1, y1, x2, y2) in main_regions + sub_regions:
        numpy_img = region_of_interest(img, field, x1, y1, x2, y2)

        custom_config = r'-c tessedit_char_whitelist=0123456789.% --oem 1 --psm 7'
        pil_img = Image.fromarray(numpy_img)
        tesseract_text = ocr_pytesseract(pil_img, custom_config)
        # print(f"{field}.tesseract_text : {tesseract_text}")
        ret[field] = tesseract_text
        
        # easyocr_text = ocr_easyocr(numpy_img)
        # print(f"{field}.easyocr_text : {easyocr_text}")

    return ret

def extract_name(img):
    # キャリブレーション実施
    # region = (70, 22, 377, 76)

    numpy_img = region_of_interest(img, "charactor", 70, 22, 377, 76)

    # candidates = ["カルロッタ", "ツバキ", "ザンニー", "カカロ"]
    with open("data/charactor_names.txt", "r", encoding="utf-8") as file:
            candidates = [line.strip() for line in file if line.strip()]
    custom_config = f'-c tessedit_char_whitelist={''.join(candidates)} --oem 1 --psm 7'
    pil_img = Image.fromarray(numpy_img)
    tesseract_text = ocr_pytesseract(pil_img, custom_config, lang='jpn')
    # print(f"{field}.tesseract_text : {tesseract_text}")
    closest = difflib.get_close_matches(tesseract_text, candidates, n=1, cutoff=0.55) # cutoffを上げるとマッチしない
    # print(f"{field}.tesseract_text : {closest[0]}")
    return closest[0]

def generate_json(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = np.array(img) 

    name = extract_name(img)
    costs = extract_cost(img)
    status_names = extract_status_name(img)
    status_values = extract_status_value(img)

    result = {
        "name": name,
        "slots": {
            f"slot{i}": {
                "COST": costs[f"cost{i}"],
                "MAIN": {
                    "name": status_names[f"main-name{i}"],
                    "value": status_values[f"main-value{i}"]
                },
                "SUB": {
                    f"sub{sub}": {
                        "name": status_names[f"sub-name{i}-{sub}"],
                        "value": status_values[f"sub-value{i}-{sub}"]
                    } for sub in range(1, 6)
                }
            } for i in range(1, 6)
        }
    }
    return json.dumps(result, ensure_ascii=False, indent=4)


    
if __name__ == "__main__":
    # 画像の読み込み
    if "https://" in sys.argv[1]:
        response = requests.get(sys.argv[1])
        img = Image.open(BytesIO(response.content))
        img = np.array(img)
    else:
        img = cv2.imread(sys.argv[1])

    name = extract_name(img)
    costs = extract_cost(img)
    status_names = extract_status_name(img)
    status_values = extract_status_value(img)


    headers = ["label"] + [f"slot{i}" for i in range(1, 6)]
    data = [
        ["COST"] + [costs[f"cost{i}"] for i in range(1, 6)],
        ["MAIN"] + [f'{status_names[f"main-name{i}"]} : {status_values[f"main-value{i}"]}' for i in range(1, 6)],
    ]

    for sub in range(1, 6):
        data.append(
            [f"SUB{sub}"] + [f'{status_names[f"sub-name{i}-{sub}"]} : {status_values[f"sub-value{i}-{sub}"]}' for i in range(1, 6)]
        )     
    print(f"キャラクター名 : {name}")
    print(tabulate(data, headers=headers, tablefmt="grid", stralign="center", maxcolwidths=40))
    # print(generate_json(sys.argv[1]))