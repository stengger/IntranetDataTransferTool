@echo off
chcp 65001 >nul
:: 自动请求管理员提权，防止 keyboard 键盘钩子因权限被沙箱屏蔽
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ===================================================
    echo [系统] 已成功获得管理员权限，正在启动内网数据传输服务...
    echo ===================================================
    cd /d "%~dp0"
    python app.py
) else (
    echo ===================================================
    echo [系统] 检测到当前处于普通用户身份运行。
    echo [系统] 正在申请管理员权限，以保证 F8 全局热键 100%% 被捕获...
    echo ===================================================
    powershell -Command "Start-Process cmd -ArgumentList '/k chcp 65001 >nul && cd /d \"%~dp0.\" && python app.py' -Verb RunAs"
    exit /b
)
pause