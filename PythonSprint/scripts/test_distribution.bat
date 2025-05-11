@echo off
echo ===================================
echo DAOC Sprint Manager Distribution Test
echo ===================================

REM Change to project root
cd %~dp0..

REM Build the executable
echo Step 1: Building executable...
python scripts/build_exe.py
if errorlevel 1 (
    echo Error: Build failed
    exit /b 1
)

REM Run distribution tests
echo Step 2: Running distribution tests...
python -m pytest scripts/test_distribution.py -v
if errorlevel 1 (
    echo Error: Tests failed
    exit /b 1
)

echo ===================================
echo All tests passed! Distribution ready.
echo =================================== 