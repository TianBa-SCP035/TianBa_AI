"""
简化的数据库连接工具
"""
import pandas as pd
from typing import Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from urllib.parse import quote_plus

# 全局引擎实例
_engines = {}

def get_engine(db_config: Dict[str, Any]) -> Engine:
    """获取数据库引擎"""
    db_key = f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    
    if db_key not in _engines:
        # 对密码进行URL编码，处理特殊字符
        password = quote_plus(db_config['password'])
        _engines[db_key] = create_engine(
            f"mysql+pymysql://{db_config['user']}:{password}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            f"?charset={db_config.get('charset', 'utf8mb4')}",
            pool_pre_ping=True,     # 取连接前先 ping，自动丢弃坏连接
            pool_recycle=10800,     # 超过 3 小时（10800 秒）强制重建连接
        )
    return _engines[db_key]

def execute_query_to_df(query: str, db_config: Dict[str, Any], params: Dict[str, Any] = None) -> pd.DataFrame:
    """执行查询并返回DataFrame"""
    engine = get_engine(db_config)
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params or {})