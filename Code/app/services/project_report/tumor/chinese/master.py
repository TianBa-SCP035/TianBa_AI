# -*- coding: utf-8 -*-
# 项目报告生成主函数
import sys
from pathlib import Path

# 添加项目根目录到Python路径（确保直接运行和API调用都能正常工作）
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent.parent.parent
if str(project_root) not in sys.path: sys.path.insert(0, str(project_root))
# 添加当前目录到Python路径（确保相对导入正常工作）
if str(current_dir) not in sys.path: sys.path.insert(0, str(current_dir))

# 导入服务模块 - 使用相对导入
from .export_sql import export_sql_to_excel
from .fill_word import fill_word_template
from .add_info import annotate_b_min
from .Excel_extract.All_Flow import all_flow
from .Figure_extract.download import download_images_from_smb

# 导入配置
from config.settings import REPORT_OUT, REPORT_TEMP, REPORT_TPL, PHOTO_DIR

def main():
    """主函数：调用项目报告生成函数"""
    word_path, excel_path, final_path, end_day = generate_project_report(project_code, user_end_day)
    
    if not word_path:
        print("❌ 项目报告生成失败")

def generate_project_report(project_code, end_day=None):
    """生成项目报告"""
    # 生成文件名
    excel_filename = f"{project_code}_明细.xlsx"
    final_filename = f"{project_code}_终版.xlsx"
    word_filename = f"{project_code}_项目报告.docx"
    
    # 创建文件路径
    excel_path = Path(REPORT_TEMP) / excel_filename
    final_path = Path(REPORT_OUT) / final_filename
    word_output_path = Path(REPORT_OUT) / word_filename
    template_path = Path(REPORT_TPL) / "Mode2.docx"
    
    # 确保目录存在
    Path(REPORT_TEMP).mkdir(parents=True, exist_ok=True)
    Path(REPORT_OUT).mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. 执行 SQL → 写入 Excel
        excel_path, selected_exp_code = export_sql_to_excel(project_code, excel_path)
        
        # 2. 基于【给药方案】→"给药频率"写入明细页的"注释b"
        annotate_b_min(excel_path)
        
        # 3. 执行All_Flow流程
        if selected_exp_code is None:
            print("❌ 未获取到实验编号，无法执行All_Flow流程")
            return None, None, None, None
        
        # 执行All_Flow流程
        success, end_day, downloaded_excel_file, error_messages = all_flow(
            selected_exp_code, 
            end_day, 
            str(excel_path)
        )
        
        if not success:
            print("❌ All_Flow流程执行失败")
            for error in error_messages:
                print(f"  错误: {error}")
            return None, None, None, None
        
        # 使用下载的Excel文件路径作为终版Excel路径
        final_path = downloaded_excel_file
        print(f"➡️ 使用的结束天数：{end_day}")
        
        # 4. 下载并压缩图片（静默跳过错误）
        try:
            download_images_from_smb(selected_exp_code)
        except Exception as e:
            print(f"⚠️ 图片下载失败，但继续生成报告: {str(e)}")
        
        # 5. Excel → Word 模板替换
        fill_word_template(excel_path, template_path, word_output_path, experiment_id=selected_exp_code, photo_dir=PHOTO_DIR)
        
        print(f"🎉 项目报告生成完成！")
        return word_output_path, excel_path, final_path, end_day
        
    except Exception as e:
        print(f"❌ 生成项目报告失败: {str(e)}")
        return None, None, None, None

if __name__ == "__main__":
    # 提示用户输入项目编号
    DEFAULT_PROJECT_CODE = "25P082901"
    project_code = input(f"请输入项目编号（直接回车默认{DEFAULT_PROJECT_CODE}）：").strip()
    if not project_code:
        project_code = DEFAULT_PROJECT_CODE
    print(f"➡️ 本次使用项目编号：{project_code}")
    
    # 提示用户输入结束天数
    user_end_day_input = input("请输入结束天数（直接回车默认自动提取）：").strip()
    user_end_day = int(user_end_day_input) if user_end_day_input else None
    print(f"➡️ 结束天数：{'用户输入' if user_end_day_input else '自动提取'}")
    
    # 调用主函数
    main()
