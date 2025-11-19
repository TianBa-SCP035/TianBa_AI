# -*- coding: utf-8 -*-
"""肿瘤-英文项目报告接口"""
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.services.project_report.tumor.english.master import generate_project_report

async def generate(request):
    """生成项目报告并返回包含文件信息的JSON响应"""
    if not request.content:
        raise HTTPException(status_code=400, detail="请求内容不能为空")
    
    project_code = request.content.get("project_code", "25P082901").strip()
    if not project_code:
        raise HTTPException(status_code=400, detail="项目编号不能为空")
    
    # 获取可选的结束天数参数
    end_day = request.content.get("end_day", None)
    if end_day is not None:
        try:
            end_day = int(end_day)
        except ValueError:
            raise HTTPException(status_code=400, detail="结束天数必须是整数")
    
    try:
        # 生成项目报告
        result = generate_project_report(project_code, end_day)
        
        # 检查返回值是否有效
        if not result or len(result) < 4:
            raise HTTPException(status_code=500, detail="项目报告生成失败")
            
        word_path, excel_path, final_path, actual_end_day = result
        
        if not word_path:
            raise HTTPException(status_code=500, detail="项目报告生成失败")
        
        # 构建文件信息
        files = {
            "word_document": {
                "exists": True,
                "name": f"{project_code}_Study Report.docx",
                "url": f"/api/v1/download/file?path={word_path}&filename={project_code}_Study Report.docx"
            },
            "final_excel": {
                "exists": True if final_path else False,
                "name": f"{project_code}_Final.xlsx" if final_path else "",
                "url": f"/api/v1/download/file?path={final_path}&filename={project_code}_Final.xlsx" if final_path else ""
            },
            "details_excel": {
                "exists": True if excel_path else False,
                "name": f"{project_code}_Detail.xlsx" if excel_path else "",
                "url": f"/api/v1/download/file?path={excel_path}&filename={project_code}_Detail.xlsx" if excel_path else ""
            },
            "images_zip": {
                "exists": True,  # 返回占位图片
                "name": f"占位表情包_Peppa.jpg",
                "url": f"/api/v1/download/file?path={Path(__file__).parent.parent.parent.parent.parent / 'public' / 'Peppa.jpg'}&filename=Peppa.jpg"
            }
        }
        
        # 返回包含文件信息的JSON响应
        return {
            "success": True,
            "message": "项目报告生成成功",
            "project_code": project_code,
            "end_day": actual_end_day,
            "files": files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成项目报告失败: {str(e)}")