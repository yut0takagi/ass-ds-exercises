from __future__ import annotations

import re
import time
from io import StringIO
from typing import List, Optional

import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ============ 設定 ============
BASE = "https://finance.yahoo.co.jp/quote/{ticker}/history"
# クラス末尾が変わっても拾える部分一致セレクタ
TABLE_CSS = "table[class*='StocksEtfReitPriceHistory__historyTable'][class*='HistoryTable']"


# ===== クリーナー（表→正規化DataFrame） =====
JP_COL_MAP = {
    "日付": "date",
    "始値": "open",
    "高値": "high",
    "安値": "low",
    "終値": "close",
    "出来高": "volume",
    "調整後終値": "adj_close",  # 「調整後終値*」にも対応（後段で*除去）
}

def _normalize_colname(col: str) -> str:
    col = str(col).strip()
    col = re.sub(r"\*$", "", col)  # 末尾の*を除去
    return col

def _jp_date_to_datetime(s: str) -> pd.Timestamp | None:
    if s is None:
        return None
    s = str(s).strip()
    m = re.match(r"^\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日\s*$", s)
    if not m:
        return pd.to_datetime(s, errors="coerce")
    y, mo, d = map(int, m.groups())
    try:
        return pd.Timestamp(year=y, month=mo, day=d)
    except Exception:
        return None

def _to_number(x):
    if x is None:
        return None
    s = str(x).strip()
    if s in ("", "-", "—", "ー", "NaN", "nan", "None"):
        return None
    s = s.replace(",", "").replace("，", "").replace("％", "%").replace("%", "")
    try:
        if "." in s:
            return float(s)
        return int(s)
    except Exception:
        try:
            return float(s)
        except Exception:
            return None

def parse_price_table_to_df(table_html: str) -> pd.DataFrame:
    raw = pd.read_html(StringIO(table_html))[0]  # FutureWarning回避のためStringIO経由

    # 列名マッピング（日本語→英語）
    cols = []
    for c in raw.columns:
        orig = _normalize_colname(c)
        mapped = None
        for jp_head, en in JP_COL_MAP.items():
            if orig.startswith(jp_head):
                mapped = en
                break
        cols.append(mapped or orig)
    raw.columns = cols

    df = raw.copy()

    # 日付→datetime
    if "date" in df.columns:
        df["date"] = df["date"].apply(_jp_date_to_datetime)

    # 数値化
    for col in ["open", "high", "low", "close", "adj_close"]:
        if col in df.columns:
            df[col] = df[col].apply(_to_number).astype("float64")
    if "volume" in df.columns:
        df["volume"] = df["volume"].apply(_to_number).astype("Int64")

    # 不要行除去・並び替え
    if "date" in df.columns:
        df = df[~df["date"].isna()]
        df = df.sort_values("date", ascending=False)

    prefer = ["date", "open", "high", "low", "close", "volume", "adj_close"]
    ordered = [c for c in prefer if c in df.columns] + [c for c in df.columns if c not in prefer]
    return df[ordered].reset_index(drop=True)


# ===== Seleniumユーティリティ =====
def build_driver(headless: bool = True) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,2000")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def page_url(ticker: str, date_from: str, date_to: str, timeframe: str, page: int) -> str:
    # timeframe: d=日足, w=週足, m=月足
    return f"{BASE}?styl=stock&from={date_from}&to={date_to}&timeFrame={timeframe}&page={page}".format(ticker=ticker)

def wait_table(driver: webdriver.Chrome, timeout: int = 15) -> None:
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, TABLE_CSS))
    )

def fetch_clean_df_from_dom(driver: webdriver.Chrome) -> Optional[pd.DataFrame]:
    soup = BeautifulSoup(driver.page_source, "lxml")
    table = soup.select_one(TABLE_CSS)
    if table is None:
        return None
    return parse_price_table_to_df(str(table))


# ===== クロール本体（途中でも部分保存） =====
def crawl_history_and_save(
    ticker: str,
    date_from: str,
    date_to: str,
    out_csv: str,
    timeframe: str = "d",
    max_pages: int = 300,
    headless: bool = True,
    checkpoint_every: int = 5,
) -> pd.DataFrame:
    driver = build_driver(headless=headless)
    dfs: List[pd.DataFrame] = []
    partial_path = out_csv.replace(".csv", ".partial.csv")
    last_top_key: Optional[str] = None

    try:
        for page in range(1, max_pages + 1):
            url = page_url(ticker, date_from, date_to, timeframe, page)
            driver.get(url)
            try:
                wait_table(driver, timeout=12)
            except TimeoutException:
                print(f"[WARN] テーブル待機タイムアウト: page={page} → 打ち切り")
                break

            df = fetch_clean_df_from_dom(driver)
            if df is None or df.empty:
                print(f"[INFO] 空ページ: page={page} → 打ち切り")
                break

            # 同一ページ循環の簡易検出（先頭日付で判定）
            top_key = str(df.iloc[0]["date"])
            if last_top_key is not None and top_key == last_top_key:
                print(f"[INFO] 同一ページ検出: page={page} (top={top_key}) → 打ち切り")
                break
            last_top_key = top_key

            dfs.append(df)
            print(f"[OK] page={page} 取得 (rows={len(df)})")

            # チェックポイント保存（部分結合→保存）
            if page % checkpoint_every == 0:
                partial = pd.concat(dfs, ignore_index=True)
                partial = partial.drop_duplicates().sort_values("date", ascending=False).reset_index(drop=True)
                partial.to_csv(partial_path, index=False, encoding="utf-8-sig")
                print(f"[SAVE] 部分保存: {partial_path} (rows={len(partial)})")

            time.sleep(1.0)  # マナー
    except KeyboardInterrupt:
        print("[INTERRUPT] 手動中断 → 部分保存します")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e} → 部分保存します")
    finally:
        driver.quit()
        if dfs:
            partial = pd.concat(dfs, ignore_index=True)
            partial = partial.drop_duplicates().sort_values("date", ascending=False).reset_index(drop=True)
            partial.to_csv(partial_path, index=False, encoding="utf-8-sig")
            print(f"[FINAL SAVE] 部分保存: {partial_path} (rows={len(partial)})")

    # 最終結合・保存
    if not dfs:
        print("[DONE] データなし")
        return pd.DataFrame()

    final_df = pd.concat(dfs, ignore_index=True)
    final_df = final_df.drop_duplicates().sort_values("date", ascending=False).reset_index(drop=True)
    final_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"[DONE] 完了: {out_csv} (rows={len(final_df)})")
    return final_df


# ===== 実行例 =====
if __name__ == "__main__":
    _ = crawl_history_and_save(
        ticker="4689.T",
        date_from="19900101",
        date_to="20250926",
        out_csv="data/stock_history_all.csv",
        timeframe="d",         # "d"=日足, "w"=週足, "m"=月足
        max_pages=300,
        headless=False,
        checkpoint_every=3,
    )