# -*- coding: utf-8 -*-
# 项目方案生成主函数
import sys
from pathlib import Path

# 添加项目根目录到Python路径（确保直接运行和API调用都能正常工作）
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent.parent.parent
if str(project_root) not in sys.path: sys.path.insert(0, str(project_root))
# 添加当前目录到Python路径（确保相对导入正常工作）
if str(current_dir) not in sys.path: sys.path.insert(0, str(current_dir))

# 导入服务模块 - 使用相对导入
from export_sql_service import export_sql_to_excel
from fill_word_service import fill_word_template
from add_info_service import annotate_b_min
from config.settings import PLAN_OUT, PLAN_TEMP, PLAN_TPL
from app.utils.Translate.single_excel import translate_excel_region

def generate_project_plan(project_code):
    # 生成文件名
    excel_filename = f"{project_code}_英文明细.xlsx"
    word_filename = f"{project_code}_Study Protocol.docx"
    # 创建临时文件路径
    excel_path = Path(PLAN_TEMP) / excel_filename
    word_output_path = Path(PLAN_OUT) / word_filename
    # 模板路径
    template_path = Path(PLAN_TPL) / "English Tumor.docx"
    
    # 确保目录存在
    Path(PLAN_TEMP).mkdir(parents=True, exist_ok=True)
    Path(PLAN_OUT).mkdir(parents=True, exist_ok=True)
    
    try:
        # 2. 执行 SQL → 写入 Excel（竖向）
        result_excel_path = export_sql_to_excel(project_code, excel_path)
        
        # 3. 基于【给药方案】→"给药频率"写入明细页的"注释b"
        try:
            annotate_b_min(result_excel_path)
        except Exception:
            print(f"⚠️ 注释b添加失败")
        
        # 4. 翻译Excel中"明细"和"受试品信息"工作表
        try:
            translate_excel_region(result_excel_path, "明细", 2, 50, "B", "B")
        except Exception:
            print(f"⚠️ 明细翻译失败")
        try:
            translate_excel_region(result_excel_path, "受试品信息", 2, 50, "A", "X")
        except Exception:
            print(f"⚠️ 受试品信息翻译失败")
        
        # 5. Excel → Word 模板替换
        fill_word_template(result_excel_path, template_path, word_output_path)
        print(f"🎉 项目方案生成完成！")
        
        return  word_output_path , excel_path
        
    except Exception as e:
        print(f"❌ 生成项目方案失败")

if __name__ == "__main__":
    # 提示用户输入项目编号
    project_code = input("请输入项目编号（直接回车默认25P1186）：").strip()
    if not project_code:
        project_code = "25P1186" 
    print(f"➡️ 本次使用项目编号：{project_code}")
    
    # 调用生成函数
    generate_project_plan(project_code)