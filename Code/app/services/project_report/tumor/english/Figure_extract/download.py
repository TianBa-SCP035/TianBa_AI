import os
import sys
import pathlib
import shutil
from smb.SMBConnection import SMBConnection
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到Python路径
current_dir = pathlib.Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent
if str(current_dir) not in sys.path: sys.path.insert(0, str(current_dir))
# 导入配置和模块
from config.settings import SMB_CONFIG, PHOTO_DIR
from app.services.project_report.tumor.english.Figure_extract.reduction import compress_experiment_images

def download_images_from_smb(folder_name):
    """
    从SMB共享目录下载指定文件夹中的图片
    按照实验编号创建文件夹结构：Photo/实验编号/图片类型
    支持下载：动物图片、肿瘤图片、解剖图片、脏器图片
    """
    # 从配置文件获取SMB连接参数
    server_ip = SMB_CONFIG['server_ip']
    share_name = SMB_CONFIG['share_name']
    base_path = SMB_CONFIG['base_path']
    username = SMB_CONFIG['username']
    password = SMB_CONFIG['password']
    
    # 本地保存路径 - 在Photo文件夹下按实验编号创建子文件夹
    photo_dir = PHOTO_DIR
    experiment_dir = os.path.join(photo_dir, folder_name)
    
    # 图片类型映射（远程文件夹名: 本地文件夹名）
    image_types = {
        "动物图片": "mouse",
        "肿瘤图片": "tumor",
        "解剖图片": "anatomy",
        "脏器图片": "organ"
    }
    
    # 确保Photo文件夹存在
    os.makedirs(photo_dir, exist_ok=True)
    
    # 清空并重新创建实验编号文件夹
    if os.path.exists(experiment_dir):
        shutil.rmtree(experiment_dir)
    os.makedirs(experiment_dir, exist_ok=True)
    
    # 创建所有图片类型的子文件夹
    for local_folder in image_types.values():
        os.makedirs(os.path.join(experiment_dir, local_folder), exist_ok=True)
    
    # 目标文件夹路径
    target_folder_path = f"{base_path}/{folder_name}"
    
    # 下载所有类型的图片
    total_count = 0
    for remote_folder, local_folder in image_types.items():
        count = download_folder_files(server_ip, username, password, share_name, 
                                    f"{target_folder_path}/{remote_folder}", 
                                    os.path.join(experiment_dir, local_folder))
        total_count += count
    
    # 打印下载结果
    if total_count > 0:
        print(f"✅ 下载完成! 共下载 {total_count} 个文件")
        # 下载完成后自动压缩图片
        compress_experiment_images(folder_name, PHOTO_DIR)
    else:
        print("⚠️ 未找到任何图片文件")

def download_folder_files(server_ip, username, password, share_name, remote_folder_path, local_folder_path):
    """
    下载指定文件夹中的所有文件（使用多线程）
    """
    # 获取文件列表
    files = []
    conn = None
    try:
        conn = SMBConnection(username, password, 'client', server_ip)
        conn.connect(server_ip, 139)
        items = conn.listPath(share_name, remote_folder_path)
        files = [item.filename for item in items if item.filename not in ['.', '..'] and not item.isDirectory]
    except:
        return 0
    finally:
        if conn:
            conn.close()
    
    if not files:
        return 0
    
    # 多线程下载文件
    def download_single_file(filename):
        conn = None
        try:
            conn = SMBConnection(username, password, 'client', server_ip)
            conn.connect(server_ip, 139)
            remote_file_path = f"{remote_folder_path}/{filename}"
            local_file_path = os.path.join(local_folder_path, filename)
            with open(local_file_path, 'wb') as local_file:
                conn.retrieveFile(share_name, remote_file_path, local_file)
            return True
        except:
            return False
        finally:
            if conn:
                conn.close()
    
    # 使用线程池下载，最多5个线程
    success_count = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(download_single_file, files)
        success_count = sum(1 for result in results if result)
    
    return success_count

if __name__ == "__main__":
    folder_name = "25P082901"  # 可以修改为您需要查找的文件夹名称
    print(f"开始下载文件夹 {folder_name} 中的图片...")
    download_images_from_smb(folder_name)