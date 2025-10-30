import pandas as pd
import re

def wareki_to_seireki(wareki: str) -> int:
    """
    和暦を西暦に変換(昭和~令和, 1926~)
    """
    # 昭和
    if wareki.startswith("昭和"):
        year = int(re.sub(r"\D", "", wareki))  # 数字抽出
        return 1925 + year  # 昭和1年 = 1926年 → 1925 + x

    # 平成
    elif wareki.startswith("平成"):
        year = int(re.sub(r"\D", "", wareki))
        return 1988 + year  # 平成1年 = 1989年 → 1988 + x

    # 令和
    elif wareki.startswith("令和"):
        year = int(re.sub(r"\D", "", wareki))
        return 2018 + year  # 令和1年 = 2019年 → 2018 + x
    
    else:
        raise ValueError("Unknown era format: " + wareki)

