"""主启动文件,同时启动项目方案API和项目报告API服务"""
import subprocess
import sys
from pathlib import Path

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path: sys.path.insert(0, str(project_root))

def start_services():
    """启动项目方案API和项目报告API服务"""
    print("正在启动TianBa AI API服务...")
    
    # 启动项目方案API服务
    plan_process = subprocess.Popen([
        sys.executable, "app/api/v1/plan_api.py"
    ], cwd=project_root)
    
    # 启动项目报告API服务
    report_process = subprocess.Popen([
        sys.executable, "app/api/v1/report_api.py"
    ], cwd=project_root)
    
    print("服务启动完成!")
    print("项目方案API: http://localhost:6001")
    print("项目报告API: http://localhost:6002")
    print("按Ctrl+C停止所有服务")
    
    try:
        # 等待子进程结束
        plan_process.wait()
        report_process.wait()
    except KeyboardInterrupt:
        print("\n正在停止服务...")

if __name__ == "__main__":
    start_services()