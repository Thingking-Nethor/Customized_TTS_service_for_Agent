<<<<<<< HEAD
cd /d "D:\GPT-SoVITS\GPT-SoVITS-v2pro-20250604-nvidia50"
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "D:\GPT-SoVITS\GPT-SoVITS-v2pro-20250604-nvidia50"
set "PATH=%SCRIPT_DIR%\runtime;%PATH%"
runtime\python.exe -I api_v2.py
=======
chcp 65001
cd /d "D:\GPT-SoVITS\GPT-SoVITS-v2pro-20250604-nvidia50" || (
    echo [ERROR] 无法切换到目录 D:\GPT-SoVITS\GPT-SoVITS-v2pro-20250604-nvidia50
    echo 请确认 GPT-SoVITS 已安装在该路径下
    pause
    exit /b 1
)
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "D:\GPT-SoVITS\GPT-SoVITS-v2pro-20250604-nvidia50"
set "PATH=%SCRIPT_DIR%\runtime;%PATH%"
if not exist "runtime\python.exe" (
    echo [ERROR] 未找到 runtime\python.exe
    echo 请确认 GPT-SoVITS 的 runtime 环境完整
    pause
    exit /b 1
)
runtime\python.exe -I api_v2.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] api_v2.py 启动失败，错误码: %ERRORLEVEL%
    pause
)
>>>>>>> eece9ea (连接远程仓库)
