import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import unquote
from threading import local

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# 线程本地存储，用于保存请求体数据
_thread_local = local()


class APILoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, log_dir: str = "logs"):
        super().__init__(app)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.app_name = self._identify_app_name(app)
    
    def _identify_app_name(self, app) -> str:
        """识别API类型"""
        # 检查应用标题
        if hasattr(app, 'title'):
            title = getattr(app, 'title', '').lower()
            if 'report' in title:
                return 'project-report'
            if 'plan' in title:
                return 'project-plan'
        
        # 检查路由路径
        if hasattr(app, 'routes'):
            for route in getattr(app, 'routes', []):
                if hasattr(route, 'path'):
                    path = getattr(route, 'path', '').lower()
                    if 'report' in path:
                        return 'project-report'
                    if 'project-plan' in path:
                        return 'project-plan'
        
        return 'unknown'
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        
        # 创建日志条目
        original_url = str(request.url)
        log_entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": self._get_client_ip(request),
            "duration": round(time.time() - start_time, 2),
            "method": request.method,
            "status": response.status_code
        }
        
        # 判断是否是下载请求
        is_download = 'download/file' in original_url
        
        if is_download:
            # 下载请求：处理URL，提取文件名
            if 'filename=' in original_url:
                if match := re.search(r'filename=([^&]+)', original_url):
                    log_entry["url"] = unquote(match.group(1))
            else:
                log_entry["url"] = original_url
        elif hasattr(_thread_local, 'request_body_data'):
            # 非下载请求且有请求体：格式化请求体信息
            body_data = _thread_local.request_body_data
            if isinstance(body_data, dict):
                disease = body_data.get("disease", "")
                language = body_data.get("language", "")
                project_code = body_data.get("content", {}).get("project_code", "")
                
                # 格式化为 "disease-language-project_code"
                if disease and language and project_code:
                    log_entry["info"] = f"{disease}-{language}-{project_code}"
                elif disease and language:
                    log_entry["info"] = f"{disease}-{language}"
                elif disease:
                    log_entry["info"] = disease
                else:
                    log_entry["info"] = str(body_data)
            else:
                log_entry["info"] = str(body_data)
            
            # 清理线程本地存储
            delattr(_thread_local, 'request_body_data')
        
        # 保存原始URL用于判断请求类型
        log_entry["original_url"] = original_url
            
        self._write_log(log_entry)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        if forwarded_for := request.headers.get("x-forwarded-for"):
            return forwarded_for.split(",")[0].strip()
        
        if real_ip := request.headers.get("x-real-ip"):
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _write_log(self, log_entry: Dict[str, Any]):
        """写入日志到文件"""
        try:
            original_url = log_entry.get("original_url", "")
            
            # 获取API类型
            api_type = self.app_name
            if api_type == 'unknown':
                # 从URL路径提取API类型
                if "/" in original_url:
                    path_parts = [p for p in original_url.split("/") if p and ":" not in p]
                    for part in path_parts:
                        if part.lower() not in ["api", "v1", "v2", "v3"]:
                            api_type = part
                            break
            
            # 特殊处理：下载文件请求归类到project-report
            if api_type == 'download' and ':6002' in original_url:
                api_type = 'project-report'
            
            # 特殊处理：project-plan请求
            if api_type == 'unknown' and 'project-plan' in original_url:
                api_type = 'project-plan'
            
            # 写入日志文件
            month_str = datetime.now().strftime("%Y-%m")
            log_file = self.log_dir / f"{api_type}_{month_str}.log"
            
            # 创建要写入的日志条目副本，移除original_url字段
            write_entry = log_entry.copy()
            if "original_url" in write_entry:
                del write_entry["original_url"]
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(write_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"写入日志失败: {e}")


def log_request_body(body_data: Optional[Dict[str, Any]] = None):
    """全局函数：记录请求体数据到线程本地存储"""
    _thread_local.request_body_data = body_data or {}
