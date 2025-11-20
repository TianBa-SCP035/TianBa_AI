#上传GitHub用，仅占位。
#应该命名为settings.py
"""系统配置文件"""
from pathlib import Path

# 注意：Path对象的/操作符是跨平台的，会在不同操作系统上自动转换为正确的路径分隔符
# Windows上是\，Linux上是/，所以使用Path对象可以确保代码在Linux服务器上正常运行
PROJECT_ROOT = Path(__file__).parent.parent

# 数据库配置
PROJECT_DB = {
    "host": "歪比巴伯",
    "port": 3306,
    "database": "哈基米",
    "user": "南北绿豆",
    "password": "阿西嘎",
    "charset": "utf8mb4"
}

SUPPLIES_DB = {
    "host": "歪比巴伯",
    "port": 3306,
    "database": "嗯哼",
    "user": "哈基米",
    "password": "阿西嘎",
    "charset": "utf8mb4"
}

# 文件路径配置
# 项目方案相关路径
PLAN_OUT = PROJECT_ROOT / "docs" / "output" / "project_plan"
PLAN_TEMP = PROJECT_ROOT / "docs" / "temp" / "project_plan"
PLAN_TPL = PROJECT_ROOT / "docs" / "templates" / "project_plan"

# 项目报告相关路径
REPORT_OUT = PROJECT_ROOT / "docs" / "output" / "project_report"
REPORT_TEMP = PROJECT_ROOT / "docs" / "temp" / "project_report"
REPORT_TPL = PROJECT_ROOT / "docs" / "templates" / "project_report"

# 确保目录存在
PLAN_OUT.mkdir(parents=True, exist_ok=True)
PLAN_TEMP.mkdir(parents=True, exist_ok=True)
PLAN_TPL.mkdir(parents=True, exist_ok=True)
REPORT_OUT.mkdir(parents=True, exist_ok=True)
REPORT_TEMP.mkdir(parents=True, exist_ok=True)
REPORT_TPL.mkdir(parents=True, exist_ok=True)

# API配置
API_HOST = "0.0.0.0"
API_RELOAD = True

# 不同服务的端口配置
PROJECT_PLAN_API_PORT = 6001  # 项目方案API端口
PROJECT_REPORT_API_PORT = 6002  # 项目报告API端口
MAIN_API_PORT = 6000  # 主API服务端口

# DRM解密服务配置
DRM_CONFIG = {
    'server_address': '你猜',
    'port': 四位数,
    'ssl_enabled': 你再猜,
    'user_id': '就不告诉你',
    'password': '略略略'
}

# SMB连接配置 - 用于下载实验图片
SMB_CONFIG = {
    'server_ip': '嘿嘿嘿哈',
    'share_name': '曼波',
    'base_path': '/肿瘤药效部/肿瘤药效部共享/肿瘤药效组-SD共享照片',
    'username': '小帅',
    'password': '柳如烟'
}

# 图片保存路径配置
PHOTO_DIR = PROJECT_ROOT / "docs" / "temp" / "photo"
PHOTO_DIR.mkdir(parents=True, exist_ok=True)
