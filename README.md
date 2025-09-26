# DS演習課題
---
## シラバス
> [シラバスのリンク](https://room.chuo-u.ac.jp/ct/syllabus_5646175)

## 時系列解析の概要
### 0. 時系列データの収集
> LINEヤフーの株価変動(時系列データ)<br>[Yahooファイナンス](https://finance.yahoo.co.jp/quote/4689.T/history)<br>**取得期間**:2025-09-25 ~ 2001-03-30<br>※取得するデータは著作権のため、gitignoreで記述しています。以下のように、crawling.pyを実行することにより取得してください。

```bash
git clone git@github.com:yut0takagi/ass-ds-exercises.git
cd ass-ds-exercises

# 推奨: 仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存のインストール
pip install -U pip
pip install -r requirements.txt  # 無ければ下記をインストール
# pip install selenium webdriver-manager beautifulsoup4 lxml pandas

# 出力ディレクトリを作成（必須）
mkdir -p data
python notebook/crawling.py
```


### 1. 時系列データの可視化

