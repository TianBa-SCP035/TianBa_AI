from pathlib import Path
from fastapi import FastAPI
from typing import Optional
from .api_logger import APILoggingMiddleware, log_request_body


def add_api_logging(app: FastAPI, log_dir: Optional[str] = None):
    """
    为FastAPI应用添加API日志记录中间件
    
    Args:
        app: FastAPI应用实例
        log_dir: 日志目录路径，默认为Code/docs/logs
    """
    # 设置默认日志目录
    if log_dir is None:
        # 从当前文件路径推导出项目根目录
        current_file = Path(__file__)
        # 当前文件在 Code/app/utils/log_utils.py，需要向上四级到 Code 目录
        project_root = current_file.parent.parent.parent.parent
        log_dir = project_root / "docs" / "logs"
    
    # 添加中间件
    app.add_middleware(APILoggingMiddleware, log_dir=str(log_dir))