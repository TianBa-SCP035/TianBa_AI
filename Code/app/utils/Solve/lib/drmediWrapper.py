#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRM EDI Python包装器
用于调用libdrmedi.so（Linux）或DrmEdiC.dll（Windows）动态库中的函数
"""

import ctypes
import os
import platform
from ctypes import c_char_p, c_int, c_ushort, c_void_p, c_bool, c_ulong, Structure, POINTER
from ctypes.wintypes import FILETIME

class DrmediWrapper:
    """DRM EDI动态库的Python包装器"""
    
    def __init__(self, lib_path=None):
        """
        初始化包装器
        
        Args:
            lib_path (str): 动态库的路径，如果为None则尝试从默认位置加载
        """
        self.platform = platform.system().lower()
        
        if lib_path is None:
            lib_path = self._find_default_library()
        
        # 加载动态库
        if self.platform == "windows":
            self.lib = ctypes.WinDLL(lib_path)
        else:
            self.lib = ctypes.CDLL(lib_path)
        
        self._setup_functions()
    
    def _find_default_library(self):
        """
        默认的动态库路径
        """
        if self.platform == "windows":
            # Windows 默认路径
            possible_paths = [
                "./c/lib/x64/DrmEdiC.dll",
                "./c/lib/Win32/DrmEdiC.dll",
                "./DrmEdiC.dll"
            ]
        else:
            # Linux 默认路径
            possible_paths = [
                "./lib/x64",
                "./libdrmedi.so",
                "/usr/local/lib/libdrmedi.so",
                "/usr/lib/libdrmedi.so"
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError(f"无法找到{'DrmEdiC.dll' if self.platform == 'windows' else 'libdrmedi.so'}动态库")
    
    def _setup_functions(self):
        """设置函数签名"""
        
        if self.platform == "windows":
            self._setup_windows_functions()
        else:
            self._setup_linux_functions()
    
    def _setup_windows_functions(self):
        """Windows版本的函数签名"""
        
        # 定义Windows特定的类型
        WCHAR = ctypes.c_wchar
        LPCWSTR = ctypes.c_wchar_p
        LPBYTE = ctypes.POINTER(ctypes.c_ubyte)
        BOOL = ctypes.c_bool
        VOID = None
        
        # SetServerAddress(BOOL bSsl, LPCWSTR lpServer, USHORT port)
        self.lib.SetServerAddress.argtypes = [BOOL, LPCWSTR, c_ushort]
        self.lib.SetServerAddress.restype = VOID
        
        # EnableLog2Syslog(int isEnable)
        if hasattr(self.lib, "EnableLog2Syslog"):
            self.lib.EnableLog2Syslog.argtypes = [c_int]
            self.lib.EnableLog2Syslog.restype = None
        
        # Authenticate(LPCWSTR lpUserId, LPCWSTR lpPassword, LPCWSTR lpConfigPath)
        self.lib.Authenticate.argtypes = [LPCWSTR, LPCWSTR, LPCWSTR]
        self.lib.Authenticate.restype = BOOL
        
        # IsEncryptedDrmFile(LPCWSTR lpFilePath)
        self.lib.IsEncryptedDrmFile.argtypes = [LPCWSTR]
        self.lib.IsEncryptedDrmFile.restype = BOOL
        
        # GetDrmFileInfo(LPCWSTR lpFilePath, DrmFileInfo * pFileInfo)
        # 首先定义DrmFileInfo结构体
        class DrmFileInfo(Structure):
            _fields_ = [
                ("iSecretLevelId", c_int),
                ("wsOwnerId", WCHAR * 128)
            ]
        self.DrmFileInfo = DrmFileInfo
        
        self.lib.GetDrmFileInfo.argtypes = [LPCWSTR, POINTER(DrmFileInfo)]
        self.lib.GetDrmFileInfo.restype = BOOL
        
        # EncryptBasicDrmFile(LPCWSTR lpFilePath, LPCWSTR lpOwnerId, int iSecretLevelId)
        self.lib.EncryptBasicDrmFile.argtypes = [LPCWSTR, LPCWSTR, c_int]
        self.lib.EncryptBasicDrmFile.restype = c_int
        
        # EncryptAuthDrmFile(LPCWSTR lpFilePath, LPCWSTR lpOwnerId, int iSecretLevelId, ...)
        self.lib.EncryptAuthDrmFile.argtypes = [
            LPCWSTR, LPCWSTR, c_int, LPCWSTR, c_int, 
            POINTER(FILETIME), POINTER(FILETIME), BOOL, BOOL
        ]
        self.lib.EncryptAuthDrmFile.restype = c_int
        
        # EncryptWatermarkAuthFile(LPCWSTR lpFilePath, LPCWSTR lpOwnerId, ...)
        self.lib.EncryptWatermarkAuthFile.argtypes = [
            LPCWSTR, LPCWSTR, c_int, LPCWSTR, c_int,
            POINTER(FILETIME), LPCWSTR, LPCWSTR, LPCWSTR
        ]
        self.lib.EncryptWatermarkAuthFile.restype = c_int
        
        # DecryptDrmFile(LPCWSTR lpFilePath, LPCWSTR lpUserId)
        self.lib.DecryptDrmFile.argtypes = [LPCWSTR, LPCWSTR]
        self.lib.DecryptDrmFile.restype = c_int
        
        # GetDrmFilePermission(LPCWSTR lpFilePath, LPCWSTR lpUserId)
        self.lib.GetDrmFilePermission.argtypes = [LPCWSTR, LPCWSTR]
        self.lib.GetDrmFilePermission.restype = c_int
        
        # 其他Windows函数...
        self.lib.ZTEReviseShortEmploeeId.argtypes = [LPCWSTR]
        self.lib.ZTEReviseShortEmploeeId.restype = c_int
        
        self.lib.ModifySecretLevel.argtypes = [LPCWSTR, c_int]
        self.lib.ModifySecretLevel.restype = c_int
        
        self.lib.CheckDrmFileOwner.argtypes = [LPCWSTR, LPCWSTR]
        self.lib.CheckDrmFileOwner.restype = BOOL
        
        self.lib.CheckDrmFileAuthUser.argtypes = [LPCWSTR, LPCWSTR]
        self.lib.CheckDrmFileAuthUser.restype = BOOL
        
        self.lib.IsEncryptedDrmFileHeader.argtypes = [LPBYTE]
        self.lib.IsEncryptedDrmFileHeader.restype = BOOL
        
        self.lib.CanDecrypt.argtypes = [LPBYTE, LPCWSTR]
        self.lib.CanDecrypt.restype = BOOL
        
        self.lib.DecData.argtypes = [LPBYTE, c_int, LPBYTE]
        self.lib.DecData.restype = BOOL
        
        self.lib.EncData.argtypes = [LPBYTE, c_int, LPBYTE]
        self.lib.EncData.restype = BOOL
        
        # GetEncryptContext函数
        self.lib.GetEncryptContext1.argtypes = [LPBYTE, LPCWSTR, c_int]
        self.lib.GetEncryptContext1.restype = BOOL
        
        self.lib.GetEncryptContext2.argtypes = [
            LPBYTE, LPCWSTR, c_int, LPCWSTR, c_int,
            POINTER(FILETIME), POINTER(FILETIME), BOOL, BOOL
        ]
        self.lib.GetEncryptContext2.restype = BOOL
        
        self.lib.GetEncryptContext3.argtypes = [
            LPBYTE, LPCWSTR, c_int, LPCWSTR, c_int,
            POINTER(FILETIME), LPCWSTR, LPCWSTR, LPCWSTR
        ]
        self.lib.GetEncryptContext3.restype = BOOL
    
    def _setup_linux_functions(self):
        """设置Linux版本的函数签名"""
        
        # SetServerAddress(int bSsl, const char* lpServer, unsigned short port)
        self.lib.SetServerAddress.argtypes = [c_int, c_char_p, c_ushort]
        self.lib.SetServerAddress.restype = None
        
        # EnableLog2Syslog(int isEnable)
        self.lib.EnableLog2Syslog.argtypes = [c_int]
        self.lib.EnableLog2Syslog.restype = None
        
        # Authenticate(const char* lpUserId, const char* lpPassword, const char* lpConfigPath)
        self.lib.Authenticate.argtypes = [c_char_p, c_char_p, c_char_p]
        self.lib.Authenticate.restype = c_int
        
        # IsEncryptedDrmFile(char* lpFilePath)
        self.lib.IsEncryptedDrmFile.argtypes = [c_char_p]
        self.lib.IsEncryptedDrmFile.restype = c_int
        
        # EncryptBasicDrmFile(char* lpFilePath, char* lpOwnerId, int iSecretLevelId)
        self.lib.EncryptBasicDrmFile.argtypes = [c_char_p, c_char_p, c_int]
        self.lib.EncryptBasicDrmFile.restype = c_int
        
        # DecryptDrmFile(const char* lpFilePath, const char* lpUserId)
        self.lib.DecryptDrmFile.argtypes = [c_char_p, c_char_p]
        self.lib.DecryptDrmFile.restype = c_int
    
    def set_server_address(self, ssl_enabled, server_address, port):
        """
        设置服务器连接参数
        
        Args:
            ssl_enabled (bool): 是否使用SSL加密通信
            server_address (str): 服务器地址
            port (int): 服务端口
        """
        if self.platform == "windows":
            ssl_flag = 1 if ssl_enabled else 0
            self.lib.SetServerAddress(ssl_flag, server_address, port)
        else:
            ssl_flag = 1 if ssl_enabled else 0
            server_bytes = server_address.encode('utf-8')
            self.lib.SetServerAddress(ssl_flag, server_bytes, port)
    
    def enable_log_to_syslog(self, enable):
        """
        启用调试信息到syslog（仅Linux）
        Args:
            enable (bool): 是否开启日志记录
        """
        if self.platform != "windows":
            enable_flag = 1 if enable else 0
            try:
                self.lib.EnableLog2Syslog(enable_flag)
                print(f"Syslog日志记录已{'开启' if enable else '关闭'}")
            except Exception as e:
                print(f"启用syslog日志时出现异常: {e}")
        else:
            # Windows系统下直接返回，不调用动态库
            print("Windows系统不支持syslog功能，已跳过")
            return
    
    def authenticate(self, user_id, password, config_path=None):
        """
        SDK身份认证
        
        Args:
            user_id (str): 登录身份(账户)
            password (str): 登录凭证(口令)
            config_path (str): 配置文件路径（可选）
            
        Returns:
            bool: True表示认证成功，False表示认证失败
        """
        if self.platform == "windows":
            result = self.lib.Authenticate(user_id, password, config_path)
        else:
            user_id_bytes = user_id.encode('utf-8')
            password_bytes = password.encode('utf-8')
            config_path_bytes = config_path.encode('utf-8') if config_path else None
            result = self.lib.Authenticate(user_id_bytes, password_bytes, config_path_bytes)
        
        return result
    
    def is_encrypted_drm_file(self, file_path):
        """
        检查文件是否为密文
        
        Args:
            file_path (str): 待检查文件全路径
            
        Returns:
            bool: True表示是密文，False表示不是密文或文件不存在
        """
        if self.platform == "windows":
            result = self.lib.IsEncryptedDrmFile(file_path)
        else:
            file_path_bytes = file_path.encode('utf-8')
            result = self.lib.IsEncryptedDrmFile(file_path_bytes)
        
        return result
    
    def get_drm_file_info(self, file_path):
        """
        获取文件信息（仅Windows）
        
        Args:
            file_path (str): 文件全路径
            
        Returns:
            dict: 包含文件信息的字典，如果失败返回None
        """
        if self.platform == "windows":
            file_info = self.DrmFileInfo()
            result = self.lib.GetDrmFileInfo(file_path, file_info)
            
            if result:
                return {
                    "secret_level_id": file_info.iSecretLevelId,
                    "owner_id": file_info.wsOwnerId
                }
            else:
                return None
        else:
            return None
    
    def encrypt_basic_drm_file(self, file_path, owner_id, secret_level_id):
        """
        按密级加密文件
        
        Args:
            file_path (str): 文件全路径
            owner_id (str): 文件所属者Id
            secret_level_id (int): 文件密级ID
            
        Returns:
            bool: True表示加密成功，False表示加密失败
        """
        if self.platform == "windows":
            result = self.lib.EncryptBasicDrmFile(file_path, owner_id, secret_level_id)
        else:
            file_path_bytes = file_path.encode('utf-8')
            owner_id_bytes = owner_id.encode('utf-8')
            result = self.lib.EncryptBasicDrmFile(file_path_bytes, owner_id_bytes, secret_level_id)
        
        return result == 0
    
    def encrypt_auth_drm_file(self, file_path, owner_id, secret_level_id, auth_user_id, 
                             permission, start_time=None, end_time=None, 
                             support_screen_watermark=True, support_print_watermark=True):
        """
        加密带用户授权方式的文件（仅Windows）
        
        Args:
            file_path (str): 文件全路径
            owner_id (str): 文件所属者Id
            secret_level_id (int): 文件密级ID
            auth_user_id (str): 授权用户Id
            permission (int): 数据访问权限
            start_time (FILETIME): 授权开始时间，0为不限制，UTC
            end_time (FILETIME): 授权截止时间，0为不限制，UTC
            support_screen_watermark (bool): 是否支持屏幕水印
            support_print_watermark (bool): 是否支持打印水印
            
        Returns:
            bool: True表示加密成功，False表示加密失败
        """
        if self.platform == "windows":
            # 创建FILETIME结构体
            start_ft = FILETIME() if start_time is None else start_time
            end_ft = FILETIME() if end_time is None else end_time
            
            result = self.lib.EncryptAuthDrmFile(
                file_path, owner_id, secret_level_id, auth_user_id, permission,
                start_ft, end_ft, support_screen_watermark, support_print_watermark
            )
            
            return result == 0
        else:
            return False
    
    def decrypt_drm_file(self, file_path, user_id):
        """
        文件解密
        
        Args:
            file_path (str): 文件全路径
            user_id (str): 申请解密者UserId
            
        Returns:
            bool: True表示解密成功，False表示解密失败
        """
        if self.platform == "windows":
            result = self.lib.DecryptDrmFile(file_path, user_id)
        else:
            file_path_bytes = file_path.encode('utf-8')
            user_id_bytes = user_id.encode('utf-8')
            result = self.lib.DecryptDrmFile(file_path_bytes, user_id_bytes)
        
        return result == 0
    
    def get_drm_file_permission(self, file_path, user_id):
        """
        获取用户对文件的权限（仅Windows）
        
        Args:
            file_path (str): 文件全路径
            user_id (str): 使用者UserId
            
        Returns:
            int: 对文件的访问权限
        """
        if self.platform == "windows":
            permission = self.lib.GetDrmFilePermission(file_path, user_id)
            return permission
        else:
            return -1
    
    def check_drm_file_owner(self, file_path, user_id):
        """
        检查文件的Owner是否为指定用户（仅Windows）
        
        Args:
            file_path (str): 文件全路径
            user_id (str): 待匹配的Owner的UserId
            
        Returns:
            bool: True表示文档的创建者Owner为user_id，False表示不是
        """
        if self.platform == "windows":
            result = self.lib.CheckDrmFileOwner(file_path, user_id)
            return result
        else:
            return False

