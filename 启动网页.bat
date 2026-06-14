@echo off
chcp 65001 >nul
if /I not "%~1"=="--run" (
    start "IntranetDataTransferTool" cmd /k ""%~f0" --run"
    exit /b
)

cd /d "%~dp0"

set "URL=http://127.0.0.1:5000"
set "PYTHON_CMD=python"

echo ===================================================
echo [系统] 正在启动内网数据传输接收端...
echo [系统] 无需管理员权限；接收通道为粘贴/拖拽图片和天眼监控。
echo [系统] 浏览器地址：%URL%
echo ===================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo [错误] 未找到 Python。请先安装 Python，或把 Python 加入 PATH。
        goto :end
    )
    set "PYTHON_CMD=py -3"
)

%PYTHON_CMD% app.py
set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo [系统] 服务已退出，退出码：%EXIT_CODE%
if not "%EXIT_CODE%"=="0" (
    echo [提示] 常见原因：端口 5000 被占用、Flask 未安装、Python 环境不可用。
    echo [提示] 可尝试运行：pip install -r requirements.txt
)

:end
echo.
echo [系统] 按任意键关闭窗口。
pause >nul
