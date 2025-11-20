# -*- coding: utf-8 -*-
"""项目报告注释工具——用于处理给药方案数据:生成注释b、组内受试品明细串、给药信息汇总"""
import re
import sys
from pathlib import Path
import pandas as pd

# 频率映射
FREQ_MAP = {
    "QD":  "dosed once daily",
    "BID": "dosed twice daily",
    "TID": "dosed three times daily",
    "QW":  "dosed once weekly",
    "BIW": "dosed twice weekly",
    "TIW": "dosed three times weekly",
    "Q2D": "dosed once every two days",
    "Q3D": "dosed once every three days",
    "Q4D": "dosed once every four days",
    "Q5D": "dosed once every five days",
    "Q2W": "dosed once every two weeks",
}
# 给药途径映射
DOSE_ROUTE_MAP = {
    "i.p.": "intraperitoneal injection",
    "i.v.": "intravenous injection (tail vein)",
    "s.c.": "subcutaneous injection",
    "p.o.": "oral administration",
    "i.g.": "intragastric gavage",
    "i.n.": "intranasal administration",
    "i.t.": "intratumoral injection",
    "i.m.": "intramuscular injection",
}

VALID_FREQS = set(FREQ_MAP)


def normalize_dose(raw: str) -> str:
    """规范化剂量文本，确保包含mg/kg单位"""
    if not raw:
        return ""
    
    s = str(raw).strip()
    if not s:
        return ""
    
    if "mg/kg" in s.lower():
        return s
    
    # 提取数字部分
    numbers = re.findall(r"[\d.]+(?:\+[\d.]+)*", s.replace(" ", ""))
    core = numbers[0] if numbers else s
    return f"{core} mg/kg"


def sort_groups(groups):
    """按组别数字排序"""
    def extract_number(group):
        numbers = re.findall(r'\d+', group)
        return int(numbers[0]) if numbers else 0
    return sorted(groups, key=extract_number)


def generate_dose_summary(df_dose, group_col, route_col, freq_col, times_col):
    """生成给药信息汇总文本"""
    # 收集各组信息
    group_info = {}
    
    for _, row in df_dose.iterrows():
        group = row[group_col]
        if group not in group_info:
            group_info[group] = {'routes': set(), 'freqs': set(), 'times': set()}
        
        # 处理给药途径
        route = str(row.get(route_col, '')).strip()
        if route:
            route_mapped = route
            for abbr, full_name in DOSE_ROUTE_MAP.items():
                if abbr.lower() in route.lower():
                    route_mapped = full_name
                    break
            group_info[group]['routes'].add(route_mapped)
        
        # 处理给药频率
        freq = str(row.get(freq_col, '')).strip()
        if freq:
            group_info[group]['freqs'].add(freq)
        
        # 处理给药次数
        times = str(row.get(times_col, '')).strip()
        if times:
            group_info[group]['times'].add(times)
    
    # 按给药途径分组
    route_comb_groups = {}
    for group, info in group_info.items():
        route_comb = tuple(sorted(info['routes']))
        route_comb_key = '和'.join(route_comb) if len(route_comb) > 1 else route_comb[0] if route_comb else ''
        
        if route_comb_key:
            route_comb_groups.setdefault(route_comb_key, []).append(group)
    
    # 构建给药途径文本
    route_texts = []
    for route_comb, groups in route_comb_groups.items():
        unique_groups = sort_groups(list(set(groups)))
        groups_str = "、".join(unique_groups)
        
        if len(unique_groups) == len(group_info):
            route_texts.append(f"The route of administration for all groups was :{route_comb}")
        else:
            route_texts.append(f"Groups {groups_str} were dosed via :{route_comb}")
    
    # 按给药频率分组
    freq_groups = {}
    for group, info in group_info.items():
        for freq in info['freqs']:
            freq_groups.setdefault(freq, []).append(group)
    
    # 构建给药频率文本
    freq_texts = []
    for freq, groups in freq_groups.items():
        unique_groups = sort_groups(list(set(groups)))
        groups_str = "、".join(unique_groups)
        freq_desc = FREQ_MAP.get(freq.upper(), freq)
        
        if len(unique_groups) == len(group_info):
            freq_texts.append(f"For all groups :{freq_desc}")
        else:
            freq_texts.append(f"Groups {groups_str} were dosed :{freq_desc}")
    
    # 按给药次数分组
    times_groups = {}
    for group, info in group_info.items():
        for times in info['times']:
            times_groups.setdefault(times, []).append(group)
    
    # 构建给药次数文本
    times_texts = []
    for times, groups in times_groups.items():
        unique_groups = sort_groups(list(set(groups)))
        groups_str = "、".join(unique_groups)
        
        if len(unique_groups) == len(group_info):
            times_texts.append(f"All groups received {times} consecutive doses")
        else:
            times_texts.append(f"Groups {groups_str} received {times} consecutive doses")
    
    # 组合所有文本
    all_texts = []
    if route_texts:
        all_texts.append("; ".join(route_texts))
    if freq_texts:
        all_texts.append("; ".join(freq_texts))
    if times_texts:
        all_texts.append("; ".join(times_texts))
    
    return ". ".join(all_texts) + ". "


def annotate_b_min(
    excel_path: str,
    dose_sheet="给药方案",
    group_col="组别", 
    prod_col="受试品", 
    dose_col="剂量", 
    freq_col="给药频率", 
    route_col="给药途径", 
    times_col="给药次数",
    detail_sheet="明细", 
    field_col="字段名", 
    value_col="字段值",
    note_field="注释b",
    group_detail_field="组内受试品明细串",
    dose_summary_field="给药信息汇总"
) -> str:
    """处理Excel文件，生成注释b、组内受试品明细串和给药信息汇总"""
    excel_path = str(excel_path)
    if not Path(excel_path).is_file():
        raise FileNotFoundError(excel_path)

    # 读取给药方案
    df_dose = pd.read_excel(excel_path, sheet_name=dose_sheet, dtype=str)

    # 1. 生成注释b
    if freq_col not in df_dose.columns:
        raise KeyError(f"【{dose_sheet}】缺少列：{freq_col}")

    splitter = re.compile(r"[+＋,，;；]")
    seen, codes = set(), []
    for raw in df_dose[freq_col].dropna().astype(str):
        s = re.sub(r"\s+", "", raw.upper())
        for p in (x for x in splitter.split(s) if x):
            if p in VALID_FREQS and p not in seen:
                seen.add(p)
                codes.append(p)

    note_text = "; ".join([f"{c}: {FREQ_MAP[c]}" for c in codes]) + ("; " if codes else "-")

    # 2. 生成组内受试品明细串
    for col in (group_col, prod_col, dose_col):
        if col not in df_dose.columns:
            raise KeyError(f"【{dose_sheet}】缺少列：{col}")

    df_gp = df_dose[[group_col, prod_col, dose_col]].copy()
    df_gp[group_col] = df_gp[group_col].astype(str).str.strip()
    df_gp[prod_col] = df_gp[prod_col].astype(str).str.strip()
    df_gp[dose_col] = df_gp[dose_col].astype(str).str.strip()

    # 过滤空值
    df_gp = df_gp[(df_gp[group_col] != "") & (df_gp[prod_col] != "")]

    # 构建组别映射
    group_to_items = {}
    for _, r in df_gp.iterrows():
        g = r[group_col]
        p = r[prod_col]
        d = normalize_dose(r[dose_col])
        group_to_items.setdefault(g, []).append(f"{p}({d})")

    # 生成明细文本
    group_segments = [f"{g}: {'、'.join(items)}" for g, items in group_to_items.items()]
    group_detail_text = "; ".join(group_segments) if group_segments else "-"

    # 3. 生成给药信息汇总
    for col in (route_col, times_col):
        if col not in df_dose.columns:
            print(f"警告：【{dose_sheet}】缺少列：{col}，将使用空值")
    
    dose_summary_text = generate_dose_summary(df_dose, group_col, route_col, freq_col, times_col)
    
    # 4. 写回明细sheet
    df_detail = pd.read_excel(excel_path, sheet_name=detail_sheet, dtype=str)
    if field_col not in df_detail.columns or value_col not in df_detail.columns:
        raise KeyError(f"【{detail_sheet}】页缺少列：{field_col}/{value_col}")

    df_detail = df_detail.copy()

    def upsert(field_name: str, field_value: str):
        """更新或插入字段值"""
        m = (df_detail[field_col].astype(str) == field_name)
        if m.any():
            df_detail.loc[m, value_col] = field_value
        else:
            df_detail.loc[len(df_detail), [field_col, value_col]] = [field_name, field_value]

    # 更新三行数据
    upsert(note_field, note_text)
    upsert(group_detail_field, group_detail_text)
    upsert(dose_summary_field, dose_summary_text)

    # 保存文件
    with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as w:
        df_detail.to_excel(w, index=False, sheet_name=detail_sheet)

    print(f"✅ 已写入『{note_field}』")
    print(f"✅ 已写入『{group_detail_field}』")
    print(f"✅ 已写入『{dose_summary_field}』")
    
    return excel_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python add_info.py <导出的Excel路径>")
        sys.exit(1)
    annotate_b_min(sys.argv[1])
