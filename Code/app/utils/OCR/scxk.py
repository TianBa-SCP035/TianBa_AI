import os
import time
import pandas as pd
from pathlib import Path
from .search_and_download_pdf import download_certificate_by_project_number
from .pre_pdf import process_pdf
from .paddle_ocr import ocr_numbers

def process_scxk_to_excel(project_code, excel_path):
    """
    处理SCXK流程：下载PDF -> 预处理 -> OCR识别 -> 写入Excel
    
    参数:
        project_code (str): 项目编号
        excel_path (str/Path): Excel文件路径
        
    返回:
        bool: 处理是否成功
    """
    print("🔄 正在执行SCXK流程...")
    try:
        # 1. 下载PDF
        pdf_files = download_certificate_by_project_number(project_code)
        
        if not pdf_files:
            print("⚠️ 未找到相关证书文件")
            # 创建空的结果并写入Excel
            empty_result = {
                "prod": {"value": ""},
                "use": {"value": ""},
                "cert": {"value": ""}
            }
            return write_result_to_excel(excel_path, empty_result, project_code)
            
        # 收集所有PDF文件的识别结果
        all_results = {
            "prod": [],
            "use": [],
            "cert": []
        }
        
        # 处理每个PDF文件
        success_count = 0
        for pdf_path in pdf_files:
            try:
                # 2. 预处理PDF
                png_path = process_pdf(pdf_path)
                
                # 3. OCR识别
                ocr_result = ocr_numbers(png_path)
                
                # 收集识别结果
                if "prod" in ocr_result and ocr_result["prod"].get("value"):
                    all_results["prod"].append(ocr_result["prod"]["value"])
                if "use" in ocr_result and ocr_result["use"].get("value"):
                    all_results["use"].append(ocr_result["use"]["value"])
                if "cert" in ocr_result and ocr_result["cert"].get("value"):
                    all_results["cert"].append(ocr_result["cert"]["value"])
                    
                success_count += 1
                    
            except Exception:
                # 静默跳过处理失败的文件
                continue
        
        # 合并所有识别结果
        merged_result = {
            "prod": {"value": "/ ".join(all_results["prod"]) if all_results["prod"] else ""},
            "use": {"value": "/ ".join(all_results["use"]) if all_results["use"] else ""},
            "cert": {"value": "/ ".join(all_results["cert"]) if all_results["cert"] else ""}
        }
        
        # 4. 将合并结果写入Excel
        excel_success = write_result_to_excel(excel_path, merged_result, project_code)
        
        # 返回处理结果
        if excel_success:
            print(f"✅ SCXK流程执行成功：匹配到{len(pdf_files)}个文件，识别成功{success_count}个文件")
            return True
        else:
            print("⚠️ SCXK流程执行失败，但将继续后续流程")
            return False
        
    except Exception:
        print("⚠️ SCXK流程处理异常")
        # 即使处理失败，也尝试将"未找到"写入Excel
        empty_result = {
            "prod": {"value": ""},
            "use": {"value": ""},
            "cert": {"value": ""}
        }
        excel_success = write_result_to_excel(excel_path, empty_result, project_code)
        
        if excel_success:
            print("✅ SCXK流程执行成功：0个文件成功识别")
            return True
        else:
            print("⚠️ SCXK流程执行失败，但将继续后续流程")
            return False

def write_result_to_excel(excel_path, ocr_result, project_code):
    """
    将OCR结果写入Excel文件的明细sheet
    
    参数:
        excel_path (str/Path): Excel文件路径
        ocr_result (dict): OCR识别结果
        project_code (str): 项目编号
        
    返回:
        bool: 写入是否成功
    """
    try:
        # 确保Excel文件存在
        if not os.path.exists(excel_path):
            return False
            
        # 读取Excel文件的明细sheet
        df_detail = pd.read_excel(excel_path, sheet_name="明细")
        
        # 获取OCR结果，如果没有则设置为"未找到"
        prod_value = ocr_result.get("prod", {}).get("value", "")
        use_value = ocr_result.get("use", {}).get("value", "")
        cert_value = ocr_result.get("cert", {}).get("value", "")
        
        # 如果值为空，则设置为"未找到"
        prod_value = "未找到" if not prod_value else prod_value
        use_value = "未找到" if not use_value else use_value
        cert_value = "未找到" if not cert_value else cert_value
        
        # 检查是否已经存在这些数据
        existing_rows = df_detail[df_detail['字段名'].isin(['生产许可证号', '使用许可证号', '动物合格证号'])]
        
        if not existing_rows.empty:
            # 更新现有数据
            for index, row in existing_rows.iterrows():
                field_name = row['字段名']
                if   field_name == '生产许可证号':
                    df_detail.at[index, '字段值'] = prod_value
                elif field_name == '使用许可证号':
                    df_detail.at[index, '字段值'] = use_value
                elif field_name == '动物质量合格证号':
                    df_detail.at[index, '字段值'] = cert_value
        else:
            # 准备要添加的数据
            new_data = [
                {"字段名": "生产许可证号", "字段值": prod_value},
                {"字段名": "使用许可证号", "字段值": use_value},
                {"字段名": "动物合格证号", "字段值": cert_value}
            ]
            
            # 将新数据添加到DataFrame
            new_df = pd.DataFrame(new_data)
            df_detail = pd.concat([df_detail, new_df], ignore_index=True)
        
        # 使用追加模式替换明细工作表，避免文件占用问题
        with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df_detail.to_excel(writer, sheet_name="明细", index=False)
        
        return True
        
    except Exception:
        return False

if __name__ == "__main__":
    # 测试代码
    project_code = "25P0132"  # 测试项目编号
    excel_path = Path(__file__).parent.parent / f"{project_code}_明细.xlsx"  # Excel文件路径
    
    success = process_scxk_to_excel(project_code, excel_path)
    
    if success:
        print("SCXK流程处理完成！")
    else:
        print("SCXK流程处理失败！")