import sys
import cv2
import pytesseract
from PIL import Image

img = cv2.imread(sys.argv[1])
pil_img = Image.fromarray(img)
tesseract_text = pytesseract.image_to_string(img, lang='jpn', config="--oem 1 --psm 7").strip()
print(tesseract_text)

tesseract_text = pytesseract.image_to_string(img, lang='jpn', config="-c tessedit_char_whitelist=クリティカルダメージアップ重撃通常攻撃防御共鳴効率解放スキル縮焦熱電気動回折消滅 --oem 1 --psm 7").strip()
print(tesseract_text)