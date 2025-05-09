# 前提
python3がインストール済み
tesseractがインストール済み

# 開発・テスト環境
python 3.12.3 / Ubuntu 24.04 + tesseract 5.3.4

# 初期化
1. 作業フォルダを作成
    例: mkdir work
2. 作業フォルダに移動
    例: cd work
3. pythonの仮想環境を作成 
    例: python -m venv .venv
4. debugというフォルダを作成
    例: mkdir debug
5. ファイルを配置
    work/requirements.txt
    work/sample.py
6. 仮想環境をアクティベート
    source .venv/bin/activate
6. 必要ライブラリをインストール 
    例:  pip install -r requirements.txt
8. 実行
    1. URL: 
        python sample.py https://wutheringwaves-discord.kurogames-global.com/back/cd/cdac1282c66bb8e56243272d1209e1e51986fe1d.jpeg
    2. ローカルファイル: 
        wget https://wutheringwaves-discord.kurogames-global.com/back/cd/cdac1282c66bb8e56243272d1209e1e51986fe1d.jpeg
        python sample.py cdac1282c66bb8e56243272d1209e1e51986fe1d.jpeg
