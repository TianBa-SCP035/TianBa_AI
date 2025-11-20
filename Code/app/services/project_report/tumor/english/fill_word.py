from pathlib import Path
import os
import pandas as pd
from jinja2 import Environment as JinjaEnv, Undefined
from docxtpl import DocxTemplate
from .reloading import process_image_data

try:
    from jinja2.sandbox import SandboxedEnvironment as JinjaSandboxEnv
except Exception:
    JinjaSandboxEnv = None

class KeepUndefined(Undefined):
    def __str__(self):
        return f"{{{{ {self._undefined_name} }}}}"

def _build_jinja_env(sandbox=False):
    Env = JinjaSandboxEnv if sandbox and JinjaSandboxEnv else JinjaEnv
    return Env(undefined=KeepUndefined, autoescape=True)

def load_context_from_excel(excel_path, sheet_name="明细", key_col="字段名", val_col="字段值"):
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    if key_col not in df.columns or val_col not in df.columns:
        raise ValueError(f"Excel 需要包含列：{key_col} / {val_col}")
    
    context = {}
    for _, row in df.iterrows():
        key = str(row[key_col]).strip()
        val = row[val_col]
        context[key] = "" if pd.isna(val) else val
    return context

def _load_rows_from_excel(excel_path, sheet_name):
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        if df.empty:
            return []
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna("").to_dict(orient="records")
    except ValueError:
        return []

def fill_word_template(excel_path, template_path, output_path, experiment_id=None, photo_dir=None):
    # 加载基础数据
    context = load_context_from_excel(excel_path)
    
    # 加载额外工作表
    context["dose_rows"] = _load_rows_from_excel(excel_path, "给药方案")
    context["products"] = _load_rows_from_excel(excel_path, "受试品信息")
    context["form_7_1"] = _load_rows_from_excel(excel_path, "form_7_1")
    context["form_7_2"] = _load_rows_from_excel(excel_path, "form_7_2")
    context["form_7_3"] = _load_rows_from_excel(excel_path, "form_7_3")
    
    # 添加实验编号
    if experiment_id:
        context["experiment_id"] = experiment_id
    
    # 处理模板和图片
    doc = DocxTemplate(str(template_path))
    
    if experiment_id and photo_dir:
        # 处理所有类型的图片
        image_types = ["mouse", "tumor", "anatomy", "organ"]
        for folder in image_types:
            context[folder] = process_image_data(os.path.join(photo_dir, experiment_id, folder), doc)
    
    # 渲染模板
    jenv = _build_jinja_env(sandbox=True)
    try:
        doc.render(context, jinja_env=jenv)
    except TypeError:
        import docxtpl.template as tpl
        tpl.Environment = lambda *a, **k: _build_jinja_env(sandbox=False)
        if JinjaSandboxEnv:
            tpl.SandboxedEnvironment = lambda *a, **k: _build_jinja_env(sandbox=True)
        doc.render(context)
    
    # 保存文件
    output_path = Path(output_path)
    doc.save(output_path)
    print(f"✅ Word 模板替换完成")
    return output_path

if __name__ == "__main__":
    fill_word_template(
        excel_path="D:/TianBa_AI/Code/docs/temp/project_report/25P080002_明细.xlsx",
        template_path="D:/TianBa_AI/Code/docs/templates/project_report/Mode2.docx",
        output_path="D:/TianBa_AI/Code/docs/output/project_report/25P080002_项目报告.docx",
        experiment_id="25P080002",
        photo_dir="D:/TianBa_AI/Code/docs/temp/photo"
    )
