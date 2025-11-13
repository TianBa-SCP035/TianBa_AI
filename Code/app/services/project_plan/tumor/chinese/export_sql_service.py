# -*- coding: utf-8 -*-
# SQL导出服务
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path: sys.path.insert(0, str(project_root))
# 导入根目录各个模块
from app.data.project_plan.project_info import SQL_PROJECT_INFO
from app.data.project_plan.dosage_plan import SQL_DOSAGE_PLAN
from app.data.project_plan.supplies_info import SQL_SUPPLIES_INFO
from app.data.connection import execute_query_to_df
from config.settings import PROJECT_DB, SUPPLIES_DB, PLAN_TEMP

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
        width = max(min_width, min(max_len + 8, max_width))
        worksheet.set_column(i, i, width)

def export_sql_to_excel(project_code, excel_path=None):
    # 导出SQL数据到Excel,已设置默认值
    if excel_path is None: excel_path = f"{PLAN_TEMP}/{project_code}_明细.xlsx"
    excel_path = Path(excel_path)
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. 查询项目基本信息
    project_info = execute_query_to_df(
        SQL_PROJECT_INFO,
        PROJECT_DB,
        {"project_code": project_code}
    )
    
    # 获取项目ID（用于后续查询）
    if project_info.empty:
        raise ValueError(f"未找到项目编号为 {project_code} 的项目信息")
    
    project_id = project_info.iloc[0]['项目ID']
    
    # 2. 查询给药方案
    dosage_plan = execute_query_to_df(
        SQL_DOSAGE_PLAN,
        PROJECT_DB,
        {"project_id": project_id}
    )
    
    # 3. 查询受试品信息（使用与老代码相同的逻辑）
    # 使用实验编号完整匹配
    experiment_code = str(project_info.iloc[0].get("实验编号", "")).strip()  # 完整实验编号，如25P118601
    project_number = experiment_code[:-2] if len(experiment_code) > 2 else experiment_code  # 项目编号，如25P1186
    
    # 查询参数：先用完整实验编号精确匹配，若无结果则用项目编号前缀匹配
    experiment_match = f"{experiment_code}"  # 用完整实验编号匹配实验号
    project_prefix_match = f"{project_number}"   # 若无，再匹配项目编号
    
    supplies_info = execute_query_to_df(
        SQL_SUPPLIES_INFO,
        SUPPLIES_DB,
        {"full_like": experiment_match, "prefix_like": project_prefix_match}
    )
    
    # 按"名称"聚合：同名受试品的各列去重合并（浓度/规格不同会用逗号并列，相同只保留一个）
    supplies_info_agg = _aggregate_supplies_by_name(supplies_info)
    
    # 4. 写入Excel
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        # 写入全部数据
        if not project_info.empty:
            project_info.to_excel(writer, sheet_name='全部数据', index=False)
            ws_all = writer.sheets['全部数据']
            _autosize(ws_all, project_info)
            ws_all.freeze_panes(1, 0)
        
        # 写入明细页（项目信息转置）
        if not project_info.empty:
            # 将单行数据转置为两列：字段名、字段值
            detail_df = pd.DataFrame({
                '字段名': project_info.columns,
                '字段值': project_info.iloc[0].values
            })
            detail_df.to_excel(writer, sheet_name='明细', index=False)
            ws = writer.sheets['明细']
            wb = writer.book
            header_fmt = wb.add_format({"bold": True, "text_wrap": True})
            for i, col in enumerate(detail_df.columns):
                ws.write(0, i, col, header_fmt)
            _autosize(ws, detail_df)
            ws.freeze_panes(1, 0)
        
        # 写入导出信息
        note = ""
        info = pd.DataFrame({
            "导出信息": ["导出时间", "项目编号", "总行数", "备注"],
            "结果": [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), project_code, len(project_info), note],
        })
        info.to_excel(writer, index=False, sheet_name="导出信息")
        ws_info = writer.sheets["导出信息"]
        _autosize(ws_info, info)
        ws_info.freeze_panes(1, 0)
        
        # 写入给药方案
        if not dosage_plan.empty:
            # 如果有组别列，按自然排序
            if "组别" in dosage_plan.columns:
                dosage_plan = dosage_plan.sort_values(by="组别", key=_natural_sort_g)
            
            dosage_plan.to_excel(writer, sheet_name='给药方案', index=False)
            ws2 = writer.sheets['给药方案']
            _autosize(ws2, dosage_plan)
            ws2.freeze_panes(1, 0)
        
        # 写入受试品信息
        if not supplies_info.empty:
            # 聚合后的受试品信息
            supplies_info_agg.to_excel(writer, sheet_name='受试品信息', index=False)
            ws3 = writer.sheets['受试品信息']
            _autosize(ws3, supplies_info_agg)
            ws3.freeze_panes(1, 0)
    
    print(f"✅ SQL数据已导出到: {excel_path.name}")
    return str(excel_path)

if __name__ == "__main__":
    # 测试代码
    project_code = input("请输入项目编号: ").strip() or "25P1186"
    try:
        excel_path = export_sql_to_excel(project_code)
    except Exception as e: print(f"导出失败: {e}")