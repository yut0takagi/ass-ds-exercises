# 東京都外国人人口時系列データ解析 - DS演習課題

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.3-150458?logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-F7931E?logo=scikitlearn&logoColor=white)
![statsmodels](https://img.shields.io/badge/statsmodels-0.14-2E7D32)
![matplotlib](https://img.shields.io/badge/matplotlib-3.10-11557C)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

本プロジェクトは、東京都が公開している外国人人口データをもとに、データの前処理からEDA（探索的データ解析）、時系列モデリングによる将来予測までを一貫して行う**分析ワークフロー**です。

---

## 📈 プロジェクト概要

- **目的**: 東京都の外国人人口推移を様々な切り口で可視化し、将来予測モデルを構築する
- **手法**: Python, pandas, matplotlib, statsmodels, scikit-learn等を活用して時系列解析
- **流れ**:
    1. データ収集・解釈  
    2. 前処理  
    3. EDA（可視化・基礎統計）  
    4. 傾向・季節性分析  
    5. SARIMA等による予測モデル構築
    6. 結果・解釈・注意点まとめ

---

## 🚀 クイックスタート

```bash
# 仮想環境・必要パッケージのインストール
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# JupyterLab起動
jupyter lab
```

notebook/ 配下のノートブックを順に実行してください。

---

## 📂 ディレクトリ構成

- `notebook/00_pretreatment.ipynb` ... データの前処理・クリーニング
- `notebook/01_eda.ipynb` ... EDAと可視化
- `notebook/02_model.ipynb` ... モデル構築・予測・評価
- `notebook/tools.py` ... 分析用カスタムツール
- `data/` ... 各種データファイル（`README.md`に解説あり）
- `requirements.txt` ... 必要パッケージ一覧

---

## 📊 分析・モデルのポイント

- **公的統計の基準変化（2012年/2017年）に配慮**
- **時系列予測（SARIMA等）の実装例あり**
- **日本語可視化にも対応（japanize-matplotlib等）**
- **notebook間の流れを意識した設計**

---

## 📎 参考・リンク

- [データ詳細・注意点: data/README.md](data/README.md)
- [東京都 統計部 外国人人口](https://www.toukei.metro.tokyo.lg.jp/gaikoku/ga-index.htm)
- [シラバス](https://room.chuo-u.ac.jp/ct/syllabus_5646175)

---

## ⚠️ 注意・備考
- 統計制度の変更（2012・2017年等）は必ず`data/README.md`を読んでからご利用ください

---

