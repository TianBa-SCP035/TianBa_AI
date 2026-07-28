import os
import re
import sys
from datetime import datetime
from smb.SMBConnection import SMBConnection

# 添加项目根目录到 Python 路径，便于导入配置
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from config.settings import CERT_SMB_CONFIG

# 导入Hakimi模块用于解密
solve_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Solve")
sys.path.append(solve_path)
from Hakimi import drmed


def download_certificate_by_project_number(project_number):
    """
    根据项目编号从网络共享文件夹搜索并下载匹配的PDF文件
    参数:   project_number (str): 要搜索的项目编号，如'25P1156'
    返回:   list: 下载的文件路径列表
    """
    # 从配置文件读取 SMB 连接参数
    username = CERT_SMB_CONFIG['username']
    password = CERT_SMB_CONFIG['password']
    server_ip = CERT_SMB_CONFIG['server_ip']
    share_name = CERT_SMB_CONFIG['share_name']
    base_path = CERT_SMB_CONFIG['base_path']
    
    downloaded_files = []
    conn = None
    
    try:
        # 创建SMB连接
        conn = SMBConnection(username, password, 'client', server_ip)
        conn.connect(server_ip, 139)
        
        # 获取基础路径下的所有文件夹
        shared_items = conn.listPath(share_name, base_path)
        
        # 过滤出日期格式的文件夹并按日期排序（最新的在前）
        date_folders = []
        for item in shared_items:
            if item.isDirectory and re.match(r'^\d{8}$', item.filename):
                try:
                    folder_date = datetime.strptime(item.filename, '%Y%m%d')
                    date_folders.append((item.filename, folder_date))
                except ValueError:
                    continue
        
        # 按日期降序排序（最新的在前）
        date_folders.sort(key=lambda x: x[1], reverse=True)
        
        if not date_folders:
            return downloaded_files
        
        # 创建本地下载目录
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloaded_pdfs')
        os.makedirs(download_dir, exist_ok=True)
        
        # 用于跟踪已处理的文件名，避免重复
        processed_filenames = set()
        
        # 逐个文件夹搜索
        found_count = 0
        for folder_name, _ in date_folders:
            folder_path = f"{base_path}/{folder_name}"
            
            try:
                # 获取文件夹中的所有文件
                files = conn.listPath(share_name, folder_path)
                
                # 搜索匹配项目编号的PDF文件
                for file_item in files:
                    if (not file_item.isDirectory and 
                        file_item.filename.lower().endswith('.pdf') and 
                        re.search(project_number, file_item.filename, re.IGNORECASE)):
                        
                        # 检查文件名是否已经处理过
                        if file_item.filename in processed_filenames:
                            continue
                        
                        # 标记文件名为已处理
                        processed_filenames.add(file_item.filename)
                        
                        found_count += 1
                        
                        # 定义本地文件路径
                        local_path = os.path.join(download_dir, file_item.filename)
                        
                        # 检查文件是否已存在
                        if os.path.exists(local_path):
                            # 文件已存在，跳过下载
                            downloaded_files.append(local_path)
                            continue
                        
                        # 下载文件
                        remote_path = f"{folder_path}/{file_item.filename}"
                        
                        with open(local_path, 'wb') as local_file:
                            conn.retrieveFile(share_name, remote_path, local_file)
                        
                        # 解密下载的PDF文件
                        # 保存原始工作目录
                        original_cwd = os.getcwd()
                        # 切换到Solve目录以确保相对路径正确
                        os.chdir(solve_path)
                        # 调用解密函数，确保参数为字符串类型
                        decrypt_result = drmed(str(local_path))
                        # 恢复原始工作目录
                        os.chdir(original_cwd)
                        
                        downloaded_files.append(local_path)
            except Exception:
                continue
            
    except Exception:
        pass
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass
    
    return downloaded_files

if __name__ == "__main__":
    # 使用简化函数
    project_number = "25P1156"  # 要搜索的项目编号
    
    # 执行搜索和下载，获取文件路径列表
    downloaded_files = download_certificate_by_project_number(project_number)
    
    print("下载的文件路径列表:")
    for file_path in downloaded_files:
        print(file_path)