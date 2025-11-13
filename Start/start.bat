@echo off
echo Going TianBa AI Backend...
start "TianBa AI Backend" cmd /k "cd /d "%~dp0..\Code" && call conda activate DICK && C:\Users\admin\.conda\envs\DICK\python.exe app\main\main.py"

timeout /t 2 /nobreak >nul

echo Going TianBa AI Frontend...
start "TianBa AI Frontend" cmd /k "cd /d "%~dp0..\Web" && pnpm dev"

exit