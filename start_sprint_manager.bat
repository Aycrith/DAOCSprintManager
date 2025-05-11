@echo off
echo DAOC Sprint Manager
echo ==================
echo Starting the sprint manager application...
echo.
echo The application will run in the system tray.
echo Right-click the tray icon for options.
echo.

python -m src.daoc_sprint_manager.main

echo.
echo Application closed. Press any key to exit.
pause > nul 