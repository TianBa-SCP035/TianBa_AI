# -*- coding: utf-8 -*-
"""注释添加服务"""
import re
import pandas as pd
from pathlib import Path
# 频率映射
FREQ_MAP = {
    "QD":  "refers to a dosing frequency of once a day",
    "BID": "refers to a dosing frequency of twice per day",
    "TID": "refers to a dosing frequency of three times per day",
    "QW":  "refers to a dosing frequency of once a week",
    "BIW": "refers to a dosing frequency of twice per week",
    "TIW": "refers to a dosing frequency of three times per week",
    "Q2D": "refers to a dosing frequency of once every two days",
    "Q3D": "refers to a dosing frequency of once every three days",
    "Q4D": "refers to a dosing frequency of once every four days",
    "Q5D": "refers to a dosing frequency of once every five days",
    "Q2W": "refers to a dosing frequency of once every two weeks",
}
VALID = set(FREQ_MAP)

def annotate_b_min(excel_path: str,
                   dose_sheet="给药方案", freq_col="给药频率",
                   detail_sheet="明细", field_col="字段名", value_col="字段值",
                   note_field="注释b") -> str:
    """基于【给药方案】→"给药频率"写入明细页的注释b"""
    excel_path = Path(excel_path)
    if not excel_path.is_file():
        raise FileNotFoundError(excel_path)

    # 1) 读取给药频率列
    df_dose = pd.read_excel(excel_path, sheet_name=dose_sheet, dtype=str)
    if freq_col not in df_dose.columns:
        raise KeyError(f"【{dose_sheet}】缺少列：{freq_col}")

    # 抽取出现过的代码（按首次出现顺序去重）
    splitter = re.compile(r"[+＋,，;；]")  # 支持多种分隔符
    seen, codes = set(), []
    for raw in df_dose[freq_col].dropna().astype(str):
        s = re.sub(r"\s+", "", raw.upper())  # 去空格统一大写
        for p in (x for x in splitter.split(s) if x):
            if p in VALID and p not in seen:
                seen.add(p)
                codes.append(p)

    # 组装注释文本（示例：QW: 每周给药一次； BIW: 每周给药两次；）
    note_text = "；".join([f"{c}：{FREQ_MAP[c]}" for c in codes]) + ("；" if codes else "-")

    # 2) 写回明细页：如果已有"注释b"则更新，否则追加一行
    df_detail = pd.read_excel(excel_path, sheet_name=detail_sheet, dtype=str)
    if field_col not in df_detail.columns or value_col not in df_detail.columns:
        raise KeyError(f"【{detail_sheet}】页缺少列：{field_col}/{value_col}")

    df_detail = df_detail.copy()
    mask = (df_detail[field_col].astype(str) == note_field)
    if mask.any():
        df_detail.loc[mask, value_col] = note_text
    else:
        df_detail = pd.concat(
            [df_detail, pd.DataFrame([{field_col: note_field, value_col: note_text}])],
            ignore_index=True
        )

    # 仅替换"明细"页，其它不动
    with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as w:
        df_detail.to_excel(w, index=False, sheet_name=detail_sheet)

    print(f"✅ 已写入注释b")
    return str(excel_path)

if __name__ == "__main__":
    # 测试代码
    excel_path = input("请输入Excel文件路径: ").strip()
    
    try:
        annotate_b_min(excel_path)
        print(f"注释添加成功: {excel_path}")
    except Exception as e:
        print(f"注释添加失败: {e}")