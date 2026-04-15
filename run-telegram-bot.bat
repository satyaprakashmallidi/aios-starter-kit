@echo off
chcp 65001 >nul
cd /d "E:\Github Projects\AIOS\aios-starter-kit\aios-starter-kit"
set PYTHONIOENCODING=utf-8
python -m apps.command.main
