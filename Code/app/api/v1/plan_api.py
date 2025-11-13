# -*- coding: utf-8 -*-
"""项目方案API应用"""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import importlib

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path: sys.path.insert(0, str(project_root))

# 导入配置
from config.settings import API_HOST, PROJECT_PLAN_API_PORT

# 创建FastAPI应用
app = FastAPI(title="TianBa AI - Project Plan API")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建API路由
router = APIRouter(prefix="/project-plan", tags=["项目方案"])

class ProjectPlanRequest(BaseModel):
    """项目方案请求模型"""
    disease: str      # 疾病模型tumor, autoimmune
    language: str     # 模板语言chinese, english
    function: Optional[str] = "generate"# 要执行的函数名，如 generate, download，默认为generate
    content: Optional[Dict[str, Any]] = None  # 请求内容，如项目编号等

# 动态执行项目方案函数
@router.post("/execute")
async def execute_project_plan_function(request: ProjectPlanRequest):
    """动态执行指定模块的指定函数"""
    # 构建模块名
    module_name = f"app.api.v1.project_plan.{request.disease}_{request.language}"
    
    try:
        # 动态导入对应模块
        module = importlib.import_module(module_name)
        # 获取要执行的函数
        if hasattr(module, request.function):
            function = getattr(module, request.function)
            # 执行函数并返回结果
            result = await function(request)
            return result
        else:
            raise HTTPException(status_code=404, detail=f"模块 {module_name} 没有函数 {request.function}")
    except ImportError:
        raise HTTPException(status_code=404, detail=f"不支持的疾病类型或语言: {request.disease}_{request.language}")

# 注册API路由
app.include_router(router)

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=PROJECT_PLAN_API_PORT)