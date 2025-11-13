# export_sql.py
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path: sys.path.insert(0, str(project_root))
# 导入SQL查询语句
from app.data.project_report.project_info import SQL_PROJECT_INFO
from app.data.project_report.dosage_plan import SQL_DOSAGE_PLAN
from app.data.project_report.supplies_info import SQL_SUPPLIES_INFO
# 导入数据库连接工具
from app.data.connection import execute_query_to_df
from config.settings import PROJECT_DB, SUPPLIES_DB, REPORT_TEMP

# —— 受试品信息合并：同名聚合、每列去重并用逗号连接 —— #
_NULLS = {"", "-", "NA", "/", "\\"}
def _normalize_cell(x) -> str:
    """把单元格转成可比较的字符串；无效值返回空串，便于后续过滤。"""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    s = str(x).strip()
    return "" if s in _NULLS else s

def _uniq_join(values, sep=", "):
    """稳定去重并连接；如果全是无效值，返回 '-'。"""
    seen = set()
    out = []
    for v in values:
        v = _normalize_cell(v)
        if not v or v in seen:
            continue
        seen.add(v)
        out.append(v)
    return sep.join(out) if out else "-"

def _aggregate_supplies_by_name(df: pd.DataFrame) -> pd.DataFrame:
    """ 按"名称"聚合：同名的记录各列做去重合并。列保序输出；如果找不到"名称"则原样返回。 """
    if df is None or df.empty or "名称" not in df.columns:
        return df
    cols = list(df.columns)
    rows = []
    for name, g in df.groupby("名称", sort=False):
        row = {"名称": name}
        for col in cols:
            if col == "名称":
                continue
            row[col] = _uniq_join(g[col].tolist())
        rows.append(row)
    return pd.DataFrame(rows, columns=cols)

def _natural_sort_g(series: pd.Series) -> pd.Series:
    """G1,G2,...,G10 自然排序；无法提取数字的放最后。"""
    s = series.astype(str).str.extract(r'(\d+)')[0].astype(float)
    return s.fillna(1e9)

def _autosize(worksheet, dataframe: pd.DataFrame, max_rows: int = 20, min_width: int = 8, max_width: int = 20):
    """根据内容长度自动列宽（上下限可调）。"""
    if dataframe is None or dataframe.empty:
        return
    for i, col in enumerate(dataframe.columns):
        values = dataframe[col].astype(str).values[:max_rows]
        max_len = max([len(str(col))] + [len(x) for x in values])
        width = max(min_width, min(max_len +8, max_width))
        worksheet.set_column(i, i, width)

def export_sql_to_excel(project_code: str, excel_path: str = None):
    # 导出SQL数据到Excel
    if excel_path is None: excel_path = f"{REPORT_TEMP}/{project_code}_明细.xlsx"
    excel_path = Path(excel_path)
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 初始化变量
    keep_raw_supplies = False  # 默认不保留原始明细
    first_row = None
    df_supplies_agg = pd.DataFrame()  # 初始化为空DataFrame

    # 1) 项目信息
    df = execute_query_to_df(SQL_PROJECT_INFO, PROJECT_DB, {"project_code": project_code})

    # 2) 明细（纵表）
    note = ""
    if df.empty:
        # 当查询结果为空时，抛出带有特定错误消息的异常
        raise ValueError("获取信息失败，请检查实验编号")
    else:
        first_row = df.iloc[0].copy()
        # 把 1.0 这种整数小数转成 1
        for col in first_row.index:
            val = first_row[col]
            if isinstance(val, float) and val.is_integer():
                first_row[col] = int(val)
        df_vertical = first_row.T.reset_index()
        df_vertical.columns = ["字段名", "字段值"]
        df_vertical["字段值"] = df_vertical["字段值"].fillna("").astype(str)

        # 3) 给药方案
        project_id = int(first_row["项目ID"])
        df_dose = execute_query_to_df(SQL_DOSAGE_PLAN, PROJECT_DB, {"project_id": project_id})
        if not df_dose.empty and "组别" in df_dose.columns:
            df_dose = df_dose.sort_values(by="组别", key=_natural_sort_g)

        # 4) 受试品信息（DB2；优先用上一个 SQL 的第一个实验编号，兜底查项目编号）
        experiment_code = str(first_row.get("实验编号", "")).strip()  # 完整实验编号，如25P118601
        project_number = experiment_code[:-2] if len(experiment_code) > 2 else experiment_code  # 项目编号，如25P1186
        
        # 查询参数：先用完整实验编号精确匹配，若无结果则用项目编号前缀匹配
        experiment_match = f"{experiment_code}"  # 用完整实验编号匹配实验号
        project_prefix_match = f"{project_number}"   # 若无，再匹配项目编号

        df_supplies = execute_query_to_df(
            SQL_SUPPLIES_INFO,
            SUPPLIES_DB,
            {"full_like": experiment_match, "prefix_like": project_prefix_match}
        )

        # 按"名称"聚合：同名受试品的各列去重合并（浓度/规格不同会用逗号并列，相同只保留一个）
        df_supplies_agg = _aggregate_supplies_by_name(df_supplies)

        # 如果想同时保留"原始明细"，就两张表都写；否则用聚合结果覆盖
        keep_raw_supplies = False  # =True 时会额外写一张"受试品明细（原始）"

    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        # 全部数据
        df.to_excel(writer, index=False, sheet_name="全部数据")
        ws_all = writer.sheets["全部数据"]
        _autosize(ws_all, df)
        ws_all.freeze_panes(1, 0)

        # 明细
        df_vertical.to_excel(writer, index=False, sheet_name="明细")
        ws = writer.sheets["明细"]
        wb = writer.book
        header_fmt = wb.add_format({"bold": True, "text_wrap": True})
        for i, col in enumerate(df_vertical.columns):
            ws.write(0, i, col, header_fmt)
        _autosize(ws, df_vertical)
        ws.freeze_panes(1, 0)

        # 导出信息
        info = pd.DataFrame({
            "导出信息": ["导出时间", "项目编号", "总行数", "备注"],
            "结果": [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), project_code, len(df), note],
        })
        info.to_excel(writer, index=False, sheet_name="导出信息")
        ws_info = writer.sheets["导出信息"]
        _autosize(ws_info, info)
        ws_info.freeze_panes(1, 0)

        # 给药方案
        df_dose.to_excel(writer, index=False, sheet_name="给药方案")
        ws2 = writer.sheets["给药方案"]
        _autosize(ws2, df_dose)
        ws2.freeze_panes(1, 0)

        # 受试品信息（新）
        if keep_raw_supplies: # （可选）原始明细
            df_supplies.to_excel(writer, index=False, sheet_name="受试品明细（原始）")
            _autosize(writer.sheets["受试品明细（原始）"], df_supplies)
            writer.sheets["受试品明细（原始）"].freeze_panes(1, 0)

        df_supplies_agg.to_excel(writer, index=False, sheet_name="受试品信息")# 聚合后的"受试品信息"（供 Word 使用）
        ws3 = writer.sheets["受试品信息"]
        _autosize(ws3, df_supplies_agg)
        ws3.freeze_panes(1, 0)

    print(f"✅ 已导出 Excel: {excel_path.name}")
    if df.empty:
        return excel_path, None
    else:
        selected_experiment_code = str(first_row["实验编号"]) if pd.notna(first_row["实验编号"]) else None
        return excel_path, selected_experiment_code

if __name__ == "__main__":
    # 测试代码
    project_code = input("请输入项目编号: ").strip() or "25P1186"
    try:
        out_path, selected_experiment_code = export_sql_to_excel(project_code)
        if selected_experiment_code: print(f"✅ 选择的实验编号: {selected_experiment_code}")
    except Exception as e: print(f"导出失败: {e}")