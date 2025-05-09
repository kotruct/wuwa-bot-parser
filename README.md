# 前提
python3がインストール済み

tesseractがインストール済み

```
sudo apt update
sudo apt tesseract-ocr python3 python3-is-python
```

WSL
```
sudo apt install tesseract-ocr python3 python3.10-venv python-is-python3
```

# 開発・テスト環境
python 3.12.3 + tesseract 5.3.4  / Ubuntu 24.04

# 準備
https://discord.com/channels/1035380212927574068/1323191401378222122

ここでデータを取得したい共鳴者の画像を生成してください。

# 使い方
## 環境構築
```
git clone https://github.com/kotruct/wuwa-bot-parser.git
cd wuwa-bot-parser
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 実行
```
python parser.py https://wutheringwaves-discord.kurogames-global.com/back/cd/{ID}.jpeg
# ダウンロード済みの場合は: python parser.py {ID}.jpeg
```
