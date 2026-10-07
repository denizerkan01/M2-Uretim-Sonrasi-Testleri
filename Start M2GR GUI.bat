@echo off
setlocal
set "PORT=8782"
set "GUI_SCRIPT=%~dp0web_gui.py"
set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe"
if not exist "%PYTHON%" set "PYTHON=pythonw"
if not exist "%GUI_SCRIPT%" (
  echo GUI file not found: "%GUI_SCRIPT%"
  pause
  exit /b 1
)

echo Restarting M2GR GUI on port %PORT%...
for /f "tokens=5" %%P in ('netstat -ano -p tcp ^| findstr /R /C:":%PORT% .*LISTENING"') do taskkill /PID %%P /F >nul 2>&1
set /a WAIT_COUNT=0
:wait_for_port
set "OLD_PID="
for /f "tokens=5" %%P in ('netstat -ano -p tcp ^| findstr /R /C:":%PORT% .*LISTENING"') do set "OLD_PID=%%P"
if not defined OLD_PID goto start_gui
set /a WAIT_COUNT+=1
if %WAIT_COUNT% GEQ 10 (
  echo Could not stop the old GUI server on port %PORT%. Close it and run this file again.
  pause
  exit /b 1
)
ping -n 2 127.0.0.1 >nul
goto wait_for_port

:start_gui
echo Starting updated GUI from "%GUI_SCRIPT%"...
start "M2GR Web GUI" "%PYTHON%" "%GUI_SCRIPT%"
set /a WAIT_COUNT=0
:wait_for_server
powershell -NoProfile -Command "try { $null=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:%PORT%/api/status' -TimeoutSec 1; exit 0 } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 goto open_gui
set /a WAIT_COUNT+=1
if %WAIT_COUNT% GEQ 20 (
  echo The GUI server did not start. Check the Python installation and try again.
  pause
  exit /b 1
)
ping -n 2 127.0.0.1 >nul
goto wait_for_server

:open_gui
start "" "http://127.0.0.1:%PORT%/?refresh=%RANDOM%%RANDOM%"
echo Updated GUI is open.
endlocal
