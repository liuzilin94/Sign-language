@echo off
echo 启动前端开发服务器...
cd /d E:\csl-recognition\recognition\front
call ..\.venv\Scripts\activate.bat
npm run dev
pause
