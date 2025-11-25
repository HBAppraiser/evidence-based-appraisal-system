@echo off
REM Market Report Generator – Smart Launcher
setlocal ENABLEDELAYEDEXPANSION
set "BASE=C:\MarketReport"
cd /d "%BASE%"

set "PYCMD="
if exist "%BASE%\python\python.exe" set "PYCMD=%BASE%\python\python.exe"
if not defined PYCMD ( where py >nul 2>nul && set "PYCMD=py -3" )
if not defined PYCMD ( where python >nul 2>nul && set "PYCMD=python" )

if not defined PYCMD (
  echo No Python found. Run FirstRun_Setup.ps1 or install Python 3.12+.
  pause
  goto :eof
)

echo Using interpreter: %PYCMD%
call %PYCMD% -c "import pandas,numpy,matplotlib,reportlab,openpyxl" 1>nul 2>nul
if errorlevel 1 (
  echo Missing dependencies; running Install_Requirements.bat ...
  call "%BASE%\Install_Requirements.bat"
  call %PYCMD% -c "import pandas,numpy,matplotlib,reportlab,openpyxl" 1>nul 2>nul
  if errorlevel 1 (
    echo Dependencies still missing. See errors above.
    pause
    goto :eof
  )
)

echo Starting GUI...
call %PYCMD% "%BASE%\v_launcher.py"
pause
endlocal
