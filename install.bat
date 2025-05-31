@echo off

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Install required packages
pip install -r requirements.txt

echo Installation complete. Activate the virtual environment using "venv\Scripts\activate".
