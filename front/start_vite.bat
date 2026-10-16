@echo off
chcp 65001 >nul
echo 启动前端服务器...
cd /d E:\csl-recognition\recognition\front
call ..\.venv\Scripts\activate.bat
echo.
echo 开始执行: npm run dev
echo.
npm run dev
echo.
echo 服务器已停止
pause
