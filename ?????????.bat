@echo off
chcp 65001 >nul
title CSL手语识别系统 - 词汇验证
color 0A

echo ========================================
echo   CSL 手语识别系统 - 词汇验证模式
echo ========================================
echo.

REM 启动模型服务
echo [1/2] 启动模型服务...
cd /d E:\csl-recognition\recognition
start "模型服务" cmd /k "call run.bat"
echo    等待模型加载...

REM 等待模型启动
echo.
echo 正在等待模型服务就绪...
ping 127.0.0.1 -n 10 >nul 2>&1

REM 打开网页
echo.
echo [2/2] 打开词汇验证页面...
start "" "E:\csl-recognition\recognition\verify_word_frontend.html"

echo.
echo ========================================
echo 启动完成！
echo ========================================
echo.
echo 请在打开的网页中进行操作
echo 后端服务: http://127.0.0.1:5001
echo.
echo 按任意键退出此窗口（模型服务继续运行）...
pause >nul
