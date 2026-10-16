@echo off
chcp 65001 >nul
echo 正在启动前端服务器...
cd /d E:\csl-recognition\recognition\front
call ..\.venv\Scripts\activate.bat
npm run dev
pause
