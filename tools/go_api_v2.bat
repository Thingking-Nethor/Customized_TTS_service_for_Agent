cd /d "D:\GPT-SoVITS\GPT-SoVITS-v2pro-20250604-nvidia50"
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "D:\GPT-SoVITS\GPT-SoVITS-v2pro-20250604-nvidia50"
set "PATH=%SCRIPT_DIR%\runtime;%PATH%"
runtime\python.exe -I api_v2.py
