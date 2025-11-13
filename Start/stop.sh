#!/bin/bash
# TianBa AI 停止脚本

PROJECT_ROOT="/home/TianBa_AI"
RUN_DIR="$PROJECT_ROOT/run"
# 可配置的端口列表
PORTS_TO_CHECK=(6000 6001 6002 8080)
# 可配置的服务PID文件列表
SERVICES_TO_STOP=(frontend backend)

echo "==== 停止 TianBa AI 服务 ===="

# 停止PID文件记录的服务
for service in "${SERVICES_TO_STOP[@]}"; do
  PID_FILE="$RUN_DIR/$service.pid"
  if [ -f "$PID_FILE" ]; then
    # 读取所有PID（可能有多个）
    PIDS=$(cat "$PID_FILE")
    echo "停止 $service 服务 (PIDs: $PIDS)"
    
    # 逐个终止每个PID
    for pid in $PIDS; do
      if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null && sleep 1
        kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null
      else
        echo "$service 进程不存在 (PID: $pid)"
      fi
    done
    
    rm -f "$PID_FILE"
  else
    echo "未找到 $service PID文件"
  fi
done

# 检查端口占用
echo "检查端口占用情况..."
occupied_ports=()

for port in "${PORTS_TO_CHECK[@]}"; do
  pid=$(lsof -ti:$port 2>/dev/null)
  [ -n "$pid" ] && occupied_ports+=("$port:$pid")
done

# 处理占用的端口
if [ ${#occupied_ports[@]} -gt 0 ]; then
  echo "发现端口被占用:"
  for item in "${occupied_ports[@]}"; do
    port=${item%:*}
    pid=${item#*:}
    echo "  端口 $port, 进程 $pid"
  done
  
  read -p "是否终止所有进程? (y/n): " choice
  [ "$choice" = "y" -o "$choice" = "Y" ] && {
    for item in "${occupied_ports[@]}"; do
      pid=${item#*:}
      kill -9 $pid 2>/dev/null && echo "已终止进程 $pid"
    done
  }
else
  echo "所有端口均未被占用"
fi

echo "==== 完成 ===="