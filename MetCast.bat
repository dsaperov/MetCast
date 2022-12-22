@echo off
set path_to_venv=""
set path_to_project=""
cmd /c "cd /d %path_to_venv%\Scripts & activate & cd %path_to_project% & python -m customization.input_producer | python main.py | python customization\output_processor.py"
pause>nul