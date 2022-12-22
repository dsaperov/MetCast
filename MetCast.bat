@echo off
set path_to_venv="D:\Google Drive\PycharmProjects\MetCast\venv"
set path_to_project="D:\Google Drive\PycharmProjects\MetCast"
cmd /c "cd /d %path_to_venv%\Scripts & activate & cd %path_to_project% & python -m customization.input_producer | python main.py | python customization\output_processor.py"
pause>nul