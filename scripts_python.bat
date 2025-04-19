@echo off
REM Переходим в папку с проектом
cd /d "D:\work\Python\The-Template"
REM Активируем виртуальное окружение (если нужно)
call venv\\Scripts\\activate
REM Запускаем Python-скрипт
python run.py
REM Оставляем консоль открытой (опционально)
pause
