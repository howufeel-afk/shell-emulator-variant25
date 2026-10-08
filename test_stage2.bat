@echo off
echo ========================================================
echo [TEST STAGE 2] CLI parameters and scripts
echo ========================================================

echo.
echo [1/3] Running with startup script:
py src\main.py --script tests\startup.txt

echo.
echo [2/3] Running with custom prompt:
echo exit | py src\main.py --prompt "custom-prompt> "

echo.
echo [3/3] Running with all arguments:
py src\main.py --vfs tests\vfs_deep.zip --prompt "full-config$ " --script tests\startup.txt

echo.
echo ========================================================
echo [DONE] Stage 2 testing finished.
echo ========================================================
pause
