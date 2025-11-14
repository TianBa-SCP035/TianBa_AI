#!/bin/bash
# TianBa AI 启动脚本

# 设置项目根目录
PROJECT_ROOT="/home/TianBa_AI"
BACKEND_DIR="$PROJECT_ROOT/Code"
FRONTEND_DIR="$PROJECT_ROOT/Web"
LOG_DIR="$PROJECT_ROOT/logs"
RUN_DIR="$PROJECT_ROOT/run"

mkdir -p "$LOG_DIR" "$RUN_DIR"

# 启动前端
cd "$FRONTEND_DIR" && nohup serve -s dist -l 8080 > "$LOG_DIR/frontend.log" 2>&1 &
echo "前端服务已启动: http://172.16.1.148:8080"

# 启动后端
cd "$BACKEND_DIR" && nohup stdbuf -oL -eL python3 -u -m app.main.main 2>&1 | grep -iE --line-buffered '(get|post|options|http)' > "$LOG_DIR/backend.log" &
echo "项目方案已启动: http://172.16.1.148:6001"
echo "项目报告已启动: http://172.16.1.148:6002"
# 等待服务启动
sleep 2
# 获取实际监听端口的进程PID
FRONTEND_PID=$(lsof -ti:8080)
PLAN_PID=$(lsof -ti:6001)
REPORT_PID=$(lsof -ti:6002)
# 记录所有相关PID到文件
echo $FRONTEND_PID > "$RUN_DIR/frontend.pid"
echo "$PLAN_PID $REPORT_PID" > "$RUN_DIR/backend.pid"

echo "==== 启动完成 ===="
