# -*- coding: utf-8 -*-
"""Word模板填充服务"""
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from jinja2 import Environment as JinjaEnv, Undefined
try: from jinja2.sandbox import SandboxedEnvironment as JinjaSandboxEnv
except Exception: JinjaSandboxEnv = None  # 有些环境没有 sandbox 模块

# 自定义未定义变量类：未匹配占位符保留原样 {{ 变量名 }}
class KeepUndefined(Undefined):
    def __str__(self):
        return f"{{{{ {self._undefined_name} }}}}"

def _build_jinja_env(sandbox: bool = False):
    """构建带 KeepUndefined 的 Jinja 环境，默认使用沙箱环境（更安全）"""
    Env = JinjaSandboxEnv if sandbox and JinjaSandboxEnv is not None else JinjaEnv
    return Env(undefined=KeepUndefined, autoescape=True)

def load_context_from_excel(
    excel_path: str,
    sheet_name: str = "明细",
    key_col: str = "字段名",
    val_col: str = "字段值",
    keep_types: bool = True,
    na_as_empty: bool = True,
) -> Dict[str, Any]:
    """从Excel加载上下文字典"""
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    if key_col not in df.columns or val_col not in df.columns:
        raise ValueError(f"Excel 需要包含列：{key_col} / {val_col}")
    
    context: Dict[str, Any] = {}
    for _, row in df.iterrows():
        key = str(row[key_col]).strip()
        val = row[val_col]
        # 处理缺失值
        if pd.isna(val):
            val = "" if na_as_empty else None
        else:
            if not keep_types:
                val = str(val).strip()
        context[key] = val
    return context

def _load_dose_rows(excel_path: str, sheet_name: str = "给药方案"):
    """读取"给药方案"Sheet 为 list[dict]（没有或为空则返回 []）"""
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
    except ValueError:
        return []
    if df is None or df.empty:
        return []
    # 用空串替代 NaN，避免模板里出现 None
    return df.fillna("").to_dict(orient="records")

def _load_rows_from_excel(excel_path: str, sheet_name: str):
    """把某个Sheet按行读成 list[dict]；缺表/空表返回 []。"""
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
    except ValueError:
        return []
    if df is None or df.empty:
        return []
    return df.fillna("").to_dict(orient="records")

def fill_word_template(
    excel_path: str,
    template_path: str,
    output_path: str,
    **context_kwargs,
):
    """填充Word模板"""
    from docxtpl import DocxTemplate  # 延迟导入，避免全局副作用
    
    # 从 Excel 加载上下文字典
    context = load_context_from_excel(excel_path, **context_kwargs)
    
    # 同时尝试加载"给药方案"行列表，并放到 context["dose_rows"]（无则为空列表）
    context["dose_rows"] = _load_dose_rows(excel_path, sheet_name="给药方案")
    
    # 加载"受试品信息"，每一行对应一个纵向小表
    context["products"] = _load_rows_from_excel(excel_path, sheet_name="受试品信息")
    
    # 构建 Jinja 环境
    jenv = _build_jinja_env(sandbox=True)
    
    # 渲染模板
    doc = DocxTemplate(str(template_path))
    try:
        doc.render(context, jinja_env=jenv)
    except TypeError:
        # 极少数旧版不支持 jinja_env 参数 → 降级为全局补丁
        import docxtpl.template as tpl
        tpl.Environment = lambda *a, **k: _build_jinja_env(sandbox=False)
        if JinjaSandboxEnv is not None:
            tpl.SandboxedEnvironment = lambda *a, **k: _build_jinja_env(sandbox=True)
        doc.render(context)

    # 保存文件
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    print(f"✅ Word 模板替换完成")
    return output_path

if __name__ == "__main__":
    # 测试代码
    excel_path = input("请输入Excel文件路径: ").strip()
    template_path = input("请输入模板文件路径: ").strip()
    output_path = input("请输入输出文件路径: ").strip()
    
    try:
        fill_word_template(excel_path, template_path, output_path)
        print(f"填充成功: {output_path}")
    except Exception as e:
        print(f"填充失败: {e}")