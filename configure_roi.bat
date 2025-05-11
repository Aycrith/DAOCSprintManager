@echo off
echo DAOC Sprint Manager - ROI Configuration Tool
echo =============================================
echo This tool will help you configure the Region of Interest (ROI)
echo where the sprint icon appears in your game.
echo.
echo Make sure your Dark Age of Camelot client is running and visible.
echo.
echo Press any key to continue...
pause > nul

python -m src.daoc_sprint_manager.utils.roi_helper

echo.
echo Configuration complete. Press any key to exit.
pause > nul 