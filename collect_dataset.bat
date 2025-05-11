@echo off
echo ===================================
echo DAOC Sprint Manager - Dataset Collection Tool
echo ===================================
echo.

python -m daoc_sprint_manager.utils.dataset_collection_tool

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo Something went wrong. Please check that Python and all required packages are installed.
  echo.
  pause
) 