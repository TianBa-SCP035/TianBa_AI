# Python库导入
import io
import sys
import pathlib
from contextlib import redirect_stdout, redirect_stderr

# 添加当前目录到Python路径
current_dir = pathlib.Path(__file__).resolve().parent
if str(current_dir) not in sys.path: sys.path.insert(0, str(current_dir))

# 本地模块导入
from excel_download import download_project_file
from sup_info import update_supplement_info
from form_7_1 import extract_weight_for_word
from form_7_2 import extract_tumor_volume_for_word
from form_7_3 import extract_table
from add_second import process_excel_file

def capture_output(func, *args, **kwargs):
    """捕获函数执行的输出,避免重复使用io.StringIO代码"""
    with io.StringIO() as buf, redirect_stdout(buf), redirect_stderr(buf):
        return func(*args, **kwargs)

def execute_step(step_name, func, *args, is_critical=False, **kwargs):
    """执行单个步骤，统一处理错误和日志"""
    try:
        result = capture_output(func, *args, **kwargs)
        # 对于返回元组的函数，检查第一个元素（成功标志）
        if isinstance(result, tuple) and len(result) >= 1:
            success_flag = result[0]
        else:
            success_flag = bool(result)
            
        if success_flag:
            print(f"✅ {step_name}成功")
            return True, result
        else:
            error_msg = f"{step_name}失败"
            print(f"❌ {error_msg}")
            return False, error_msg
    except Exception as e:
        error_msg = f"{step_name}异常: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def all_flow(experiment_code: str, user_end_day: int = None, temp_file_path: str = None) -> tuple:
    """
    参数:实验编号、用户提供的结束天数、临时文件路径(目标文件路径)
    返回:tuple: (执行成功与否, 实际使用的结束天数, 下载的Excel文件路径, 错误消息列表)
    """
    error_messages = []
    end_day = 0
    downloaded_excel_file = None
    
    # 步骤1：下载Excel文件 - 关键步骤
    success, download_result = execute_step("下载Excel文件", download_project_file, experiment_code, is_critical=True)
    if not success:
        error_messages.append(download_result)
        return False, 0, None, error_messages
    
    # download_project_file返回的是元组(success, file_path)
    if isinstance(download_result, tuple) and len(download_result) >= 2:
        downloaded_excel_file = download_result[1]
    else:
        downloaded_excel_file = download_result
    
    # 步骤2: 更新补充信息 - 关键步骤
    success, update_result = execute_step("更新补充信息", update_supplement_info, 
                                 downloaded_excel_file, temp_file_path, user_end_day, is_critical=True)
    if not success:
        error_messages.append(update_result)
        return False, 0, downloaded_excel_file, error_messages
    
    # update_supplement_info返回的是元组(success, end_day)
    if isinstance(update_result, tuple) and len(update_result) >= 2:
        end_day = update_result[1]
    else:
        end_day = update_result
    
    if end_day == 0:
        error_msg = "无法获取有效的结束天数"
        print(f"❌ {error_msg}")
        error_messages.append(error_msg)
        return False, 0, downloaded_excel_file, error_messages
    
    # 步骤3-5: 生成各种表格 - 可选步骤，互不影响
    optional_steps = [
        ("生成form_7.1表格", extract_weight_for_word, downloaded_excel_file, temp_file_path, end_day),
        ("生成form_7.2表格", extract_tumor_volume_for_word, downloaded_excel_file, temp_file_path, end_day),
        ("生成form_7.3表格", extract_table, downloaded_excel_file, temp_file_path),
    ]
    
    for step_name, func, *args in optional_steps:
        success, step_result = execute_step(step_name, func, *args)
        if not success:
            error_messages.append(step_result)
    
    # 步骤6: 添加组合数据 - 可选步骤
    if temp_file_path:
        success, add_second_result = execute_step("执行add_second", process_excel_file, temp_file_path)
        if not success:
            error_messages.append(add_second_result)
    
    return True, end_day, downloaded_excel_file, error_messages

if __name__ == "__main__":
    # 从命令行参数获取三个参数：实验编号、结束天数、临时文件路径
    experiment_code = sys.argv[1] if len(sys.argv) > 1 else "25P080002"
    user_end_day = int(sys.argv[2]) if len(sys.argv) > 2 else None
    temp_file_path = sys.argv[3] if len(sys.argv) > 3 else "D:\\TianBa_AI\\Code\\docs\\temp\\project_report\\25P080002_明细.xlsx"
    
    print(f"执行参数: 实验编号={experiment_code}, 结束天数={user_end_day}")
    flow_success, end_day, error_messages = all_flow(experiment_code, user_end_day, temp_file_path)
    print(f"{'🎉  成功' if flow_success else '⚠️  失败'}, 实际使用的结束天数: {end_day}")
    if error_messages:
        print("错误信息:")
        for msg in error_messages:
            print(f"  - {msg}")
