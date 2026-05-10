@echo off
:: 设置字符集为 UTF-8 防止中文乱码
chcp 65001 >nul

echo ============================================================
echo    Wechat Moments Bot - 定时任务配置工具
echo ============================================================
echo.

set SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

:: 1. 查找 Python
echo [步骤 1/4] 正在寻找 Python 环境...
for /f "delims=" %%i in ('where python 2^>nul') do (
    set PYTHON_PATH=%%i
    goto :found_python
)
echo [错误] 找不到 Python！
pause
exit /b 1

:found_python
echo [OK] 找到 Python: %PYTHON_PATH%
echo.

:: 2. 读取时间
echo [步骤 2/4] 正在从 config.py 读取推送时间...
set TASK_TIME=
set _TMPFILE=%TEMP%\wechat_moments_time.txt
"%PYTHON_PATH%" -c "import importlib,sys;sys.path.insert(0,r'%SCRIPT_DIR%');cfg=importlib.import_module('config');h=cfg.SCHEDULE.get('push_hour',9);m=cfg.SCHEDULE.get('push_min',0);print(f'{h:02d}:{m:02d}')" > "%_TMPFILE%" 2>nul

if exist "%_TMPFILE%" (
  set /p TASK_TIME=<"%_TMPFILE%"
  del "%_TMPFILE%" >nul 2>&1
)
if not defined TASK_TIME (set TASK_TIME=09:00)
echo [OK] 设定运行时间为: %TASK_TIME%
echo.

:: 3. 清理旧任务
echo [步骤 3/4] 正在清理旧的任务冲突...
:: 屏蔽错误输出，因为任务不存在时报错是正常的
schtasks /delete /tn "WechatMomentsBot" /f >nul 2>&1
schtasks /delete /tn "\MyBot\WechatMomentsBot" /f >nul 2>&1
echo [OK] 旧任务已清理。
echo.

:: 4. 创建新任务
echo [步骤 4/4] 正在向系统注册新任务...
set RUNNER=%SCRIPT_DIR%\run_main.bat
echo 任务路径: \MyBot\WechatMomentsBot

:: 执行创建命令
schtasks /create /tn "\MyBot\WechatMomentsBot" /tr "\"%RUNNER%\"" /sc DAILY /st %TASK_TIME% /ru "%USERNAME%" /rl HIGHEST /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo    ✅ 定时任务已成功更新！
    echo    下次运行时间: %TASK_TIME%
    echo    所在文件夹  : 任务计划程序左侧 -> MyBot
    echo ============================================================
) else (
    echo.
    echo [❌ 错误] 任务创建失败！错误代码: %ERRORLEVEL%
)

echo.
echo 任务已执行完毕，按任意键退出...
pause >nul