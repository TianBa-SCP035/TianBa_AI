# -*- coding: utf-8 -*-
import sys
import pandas as pd

def extract_and_format(excel_path: str, sheet: str, value_name: str, add_percentage: bool = True, add_unit: str = None, middle_text: str = None) -> str:
    # 读表
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet, dtype=str)
    except Exception:
        return "无数据"
    if df.empty:
        return "无数据"

    cols = df.columns.astype(str)
    # 定位列
    grp = cols[cols.str.contains("组别", na=False)]
    val = cols[cols.str.contains(value_name, na=False, case=False)]
    if grp.empty or val.empty:
        return "无数据"
    gcol, vcol = grp[0], val[0]

    sub = df[[gcol, vcol]].astype(str).apply(lambda s: s.str.strip())
    # 过滤与排序
    sub = sub[(sub[gcol].notna()) & (sub[vcol].notna()) & (sub[gcol] != "G1")]
    if sub.empty:
        return "无数据"
    sub["_ord"] = sub[gcol].str.extract(r"(\d+)", expand=False).fillna("999999").astype(int)
    sub = sub.sort_values("_ord")

    # 处理组别显示格式
    group_list = sub[gcol].tolist()
    if len(group_list) > 4:
        groups = "、".join(group_list[:3]) + "......." + group_list[-1]
    else:
        groups = "、".join(group_list)
    
    # 根据参数处理数值格式
    if add_percentage:
        values = "、".join([f"{v}%" for v in sub[vcol].tolist()])
    else:
        if add_unit:
            values = "、".join([f"{v} {add_unit}" for v in sub[vcol].tolist()])
        else:
            values = "、".join([f"{v}" for v in sub[vcol].tolist()])
    
    # 根据是否有中间文本决定返回格式
    if middle_text:
        return f"{groups}组{middle_text}:{values}" if groups and values else "无数据"
    else:
        return f"{groups}组分别为:{values}" if groups and values else "无数据"

def extract_g1_value(excel_path: str, sheet: str, value_name: str, extract_sign_prefix: bool = True) -> str:
    try:
        # 读表并定位列
        df = pd.read_excel(excel_path, sheet_name=sheet, dtype=str)
        if df.empty:
            return "无数据"
            
        cols = df.columns.astype(str)
        grp = cols[cols.str.contains("组别", na=False)]
        val = cols[cols.str.contains(value_name, na=False, case=False)]
        if grp.empty or val.empty:
            return "无数据"
            
        # 获取G1组值
        g1_row = df[df[grp[0]].astype(str).str.strip() == "G1"]
        if g1_row.empty:
            return "无数据"
            
        value = str(g1_row[val[0]].iloc[0]).strip()
        if not value or value == "nan":
            return "无数据"
            
        # 根据参数处理值
        if extract_sign_prefix:
            import re
            match = re.match(r"^([+-]?\d*\.?\d+)", value)
            return match.group(1) if match else "无数据"
        return value
    except Exception:
        return "无数据"

def upsert_detail_field(df: pd.DataFrame, name: str, value: str) -> pd.DataFrame:
    # 更新或追加
    if df.empty or not {"字段名","字段值"}.issubset(df.columns):
        df = pd.DataFrame(columns=["字段名", "字段值"])
    mask = df["字段名"].astype(str).str.contains(name, na=False)
    if mask.any():
        df.loc[mask.idxmax(), "字段值"] = value
    else:
        df = pd.concat([df, pd.DataFrame([{"字段名": name, "字段值": value}])], ignore_index=True)
    return df

def process_excel_file(excel_path: str) -> bool:
    try:
        # 计算两个字段
        tgitv = extract_and_format(excel_path, "form_7_2", "TGITV")
        tgitw = extract_and_format(excel_path, "form_7_3", "TGITW")
        
        # 提取G1组数据
        g1_group_value = extract_g1_value(excel_path, "form_7_2", "分组天均值", extract_sign_prefix=True)
        g1_end_value = extract_g1_value(excel_path, "form_7_2", "结束天均值", extract_sign_prefix=False)
        # 提取受试组肿瘤体积数据
        test_group_volume = extract_and_format(excel_path, "form_7_2", "结束天均值", add_percentage=False, add_unit="mm³", middle_text="的受试品在相应剂量下的平均肿瘤体积为")

        # 读/写"明细"
        try:
            detail = pd.read_excel(excel_path, sheet_name="明细", dtype=str)
        except Exception:
            detail = pd.DataFrame(columns=["字段名", "字段值"])
        detail = upsert_detail_field(detail, "TGITV组合", tgitv)
        detail = upsert_detail_field(detail, "TGITW组合", tgitw)
        detail = upsert_detail_field(detail, "实际分组时肿瘤体积", g1_group_value)
        detail = upsert_detail_field(detail, "对照组平均肿瘤体积", g1_end_value)
        detail = upsert_detail_field(detail, "受试组肿瘤体积", test_group_volume)

        with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as w:
            detail.to_excel(w, sheet_name="明细", index=False)
            # 调整列宽：第一列20，第二列50
            worksheet = w.sheets["明细"]
            worksheet.column_dimensions['A'].width = 20
            worksheet.column_dimensions['B'].width = 50

        print(f"✅ 已写入TGITV组合：{tgitv}")
        print(f"✅ 已写入TGITW组合：{tgitw}")
        print(f"✅ 已写入实际分组时肿瘤体积：{g1_group_value}")
        print(f"✅ 已写入对照组平均肿瘤体积：{g1_end_value}")
        print(f"✅ 已写入受试组肿瘤体积：{test_group_volume}")
        
        return True
    except Exception as e:
        print(f"❌ 执行add_second失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 默认文件路径
    default_excel_path = "D:\\TianBa_AI\\Code\\docs\\temp\\project_report\\25P080002_明细.xlsx"
    excel_path = sys.argv[1] if len(sys.argv) > 1 else default_excel_path
    
    print(f"处理文件: {excel_path}")
    process_excel_file(excel_path)
