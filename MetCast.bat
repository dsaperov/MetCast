@echo off
cmd /c "cd /d D:\Google Drive\PycharmProjects\MetCast\venv\Scripts & activate & cd D:\Google Drive\PycharmProjects\MetCast & python -m customization.input_producer | python main.py | python customization\output_processor.py"
pause>nul