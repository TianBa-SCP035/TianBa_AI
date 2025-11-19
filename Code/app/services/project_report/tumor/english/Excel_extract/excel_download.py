import sys
import pathlib
import requests
import pandas as pd
from sqlalchemy import create_engine

# 添加项目根目录到Python路径
project_root = pathlib.Path(__file__).parent.parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path: sys.path.insert(0, str(project_root))

# 从根目录绝对导入Hakimi模块
from app.utils.Solve.Hakimi import drmed, print_result
# 导入配置
from config.settings import PROJECT_DB, REPORT_TEMP
# 从配置构建数据库连接URL
DB_URL = (
    f"mysql+pymysql://{PROJECT_DB['user']}:{PROJECT_DB['password']}"
    f"@{PROJECT_DB['host']}:{PROJECT_DB['port']}/{PROJECT_DB['database']}"
    f"?charset={PROJECT_DB['charset']}"
)

def download_project_file(experiment_code: str) -> (bool, str):
    """下载项目文件并返回文件路径"""
    sql = """
    SELECT DISTINCT
      CASE
        WHEN pf.business_system_synchronization = '1'
          THEN CONCAT('https://biocytogen-ps.oss-cn-beijing.aliyuncs.com/', orgf.file_path)
        WHEN pf.business_system_synchronization IS NULL
          THEN CONCAT('https://biocytogen-xdida-private.oss-cn-beijing.aliyuncs.com/', orgf.file_path)
        ELSE ''
      END AS url
    FROM project_file AS pf
    JOIN org_file orgf ON orgf.id = pf.file_id
    LEFT JOIN org_tag AS ot ON ot.id = pf.type
    LEFT JOIN project AS p ON p.id = pf.project_id
    WHERE ot.sname IN ('终版数据包（方案&报告）', '终版数据附件')
      AND p.snum = %(experiment_code)s
      AND (pf.business_system_synchronization = '1' OR pf.business_system_synchronization IS NULL)
    LIMIT 1;
    """

    try:
        engine = create_engine(DB_URL)
        df = pd.read_sql(sql, engine, params={"experiment_code": experiment_code})
    except Exception as e:
        print("数据库查询失败:", e)
        return False, ""
        
    if df.empty or not df.loc[0, "url"]:
        print("没有查到文件")
        return False, ""
        
    url = df.loc[0, "url"]
    suffix = pathlib.Path(url).suffix or ".bin"

    # 保存到docs/temp/project_report目录
    save_dir = REPORT_TEMP
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / f"{experiment_code}_Final{suffix}"

    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(resp.content)
        print("下载成功")
        
        # 检查并解密文件
        print("正在检查文件是否加密...")
        
        # 调用解密函数
        result = drmed(str(save_path))
        print_result(result)
        
        return True, str(save_path)
    except Exception as e:
        print("下载失败")
        return False, ""

if __name__ == "__main__":
    ok, file_path = download_project_file("25P080002")
    print("最终结果:", ok)
