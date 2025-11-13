#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import platform

# 添加Hakimi.py所在目录到Python路径
hakimi_dir = os.path.dirname(os.path.abspath(__file__))
if hakimi_dir not in sys.path: sys.path.insert(0, hakimi_dir)
# 添加项目根目录到Python路径（用于导入配置文件）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(hakimi_dir))))
if project_root not in sys.path: sys.path.insert(0, project_root)

# 使用相对导入
from lib.drmediWrapper import DrmediWrapper
# 使用绝对导入配置文件
from config.settings import DRM_CONFIG

def drmed(file_paths):
    """
    加密解密函数
    Args:
        file_paths (str or list): 单个文件路径、多个文件路径列表或文件夹路径
    Returns:
        dict: 包含操作结果的字典
            - total_files: 总文件数
            - encrypted_count: 加密文件数
            - decrypted_count: 解密文件数
            - failed_count: 失败文件数
    """
    # 初始化计数器
    result = {
        'total_files': 0,
        'encrypted_count': 0,
        'decrypted_count': 0,
        'failed_count': 0
    }
    
    # 根据操作系统查找对应的库文件路径
    current_platform = platform.system().lower()
    
    if current_platform == "windows":
        possible_paths = [
            os.path.join(hakimi_dir, "lib", "DrmEdiC.dll"),
            os.path.join(hakimi_dir, "DrmEdiC.dll")
        ]
    else:
        possible_paths = [
            os.path.join(hakimi_dir, "lib", "libdrmedi.so"),
            os.path.join(hakimi_dir, "libdrmedi.so"),
            "/usr/local/lib/libdrmedi.so",
            "/usr/lib/libdrmedi.so"
        ]
    
    lib_path = None
    for path in possible_paths:
        if os.path.exists(path):
            lib_path = path
            break
    
    if lib_path is None:
        print("错误: 未找到DRM库文件")
        return result
    
    try:
        # 初始化包装器
        drm = DrmediWrapper(lib_path)
        
        # 设置服务器连接（从配置文件读取）
        drm.set_server_address(
            ssl_enabled=DRM_CONFIG['ssl_enabled'],
            server_address=DRM_CONFIG['server_address'],
            port=DRM_CONFIG['port'],
        )
        
        # 认证（从配置文件读取）
        auth_success = drm.authenticate(
            user_id=DRM_CONFIG['user_id'],
            password=DRM_CONFIG['password'],
        )

        if not auth_success:
            print("错误: 身份认证失败，终止流程")
            return result
        
        # 处理输入参数
        if isinstance(file_paths, str):
            # 如果是字符串，可能是文件路径或文件夹路径
            if os.path.isdir(file_paths):
                # 是文件夹路径，获取文件夹内所有文件
                files_to_process = []
                for item in os.listdir(file_paths):
                    item_path = os.path.join(file_paths, item)
                    if os.path.isfile(item_path):
                        files_to_process.append(item_path)
            else:
                # 是文件路径
                files_to_process = [file_paths]
        elif isinstance(file_paths, list):
            # 是列表，处理每个路径
            files_to_process = []
            for path in file_paths:
                if os.path.isdir(path):
                    # 是文件夹路径，获取文件夹内所有文件
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        if os.path.isfile(item_path):
                            files_to_process.append(item_path)
                elif os.path.isfile(path):
                    # 是文件路径
                    files_to_process.append(path)
        else:
            print("错误: 输入参数类型不正确")
            return result
        
        result['total_files'] = len(files_to_process)
        
        if result['total_files'] == 0:
            print("没有找到需要处理的文件")
            return result
        
        # 检查所有文件的加密状态
        all_unencrypted = True
        encrypted_files = []
        
        for file_path in files_to_process:
            try:
                is_encrypted = drm.is_encrypted_drm_file(file_path)
                if is_encrypted:
                    all_unencrypted = False
                    encrypted_files.append(file_path)
            except Exception:
                # 如果检查加密状态失败，默认视为未加密
                pass
        
        # 根据文件状态决定操作
        if all_unencrypted:
            # 全部未加密，不做任何操作
            pass
        else:
            # 有文件已加密，解密已加密的文件
            for file_path in encrypted_files:
                try:
                    success = drm.decrypt_drm_file(
                        file_path=file_path,
                        user_id=DRM_CONFIG['user_id']
                    )
                    if success:
                        result['decrypted_count'] += 1
                    else:
                        result['failed_count'] += 1
                except Exception:
                    result['failed_count'] += 1
        
        return result
        
    except Exception:
        return result

def print_result(result):
    """打印处理结果"""
    print(f"总文件数: {result['total_files']}")
    print(f"加密文件数: {result['encrypted_count']}")
    print(f"解密文件数: {result['decrypted_count']}")
    print(f"失败文件数: {result['failed_count']}")

if __name__ == '__main__':
    # 命令行参数处理
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python Hakimi.py <文件路径或文件夹路径>")
        print("  python Hakimi.py <文件路径1> <文件路径2> ...")
        sys.exit(1)
    
    # 获取所有路径参数
    paths = sys.argv[1:]
    
    # 如果只有一个参数，可能是文件路径或文件夹路径
    if len(paths) == 1:
        result = drmed(paths[0])
    else:
        # 多个参数，作为文件路径列表处理
        result = drmed(paths)
    
    # 打印结果
    print_result(result)