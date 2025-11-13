# -*- coding: utf-8 -*-
"""肿瘤-英文项目方案接口"""
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.services.project_plan.tumor.english.master import generate_project_plan

async def generate(request) -> FileResponse:
    """生成项目计划并直接返回文件"""
    if not request.content:
        raise HTTPException(status_code=400, detail="请求内容不能为空")
    
    project_code = request.content.get("project_code", "25P1186").strip()
    if not project_code:
        raise HTTPException(status_code=400, detail="项目编号不能为空")
    
    try:
        # 生成项目计划
        word_path, excel_path = generate_project_plan(project_code)
        
        # 直接返回Word文件（使用FastAPI的FileResponse，相当于Flask的send_file）
        word_filename = f"{project_code}_Study Protocol.docx"
        return FileResponse(
            path=word_path,
            filename=word_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成项目计划失败: {str(e)}")