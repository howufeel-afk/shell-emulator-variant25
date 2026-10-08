@echo off
echo ========================================================
echo [TEST STAGES 4 and 5] Commands ls, cd, head, du, uptime, mv
echo ========================================================

echo.
echo Running command scenario in VFS:
py src\main.py --vfs tests\vfs_deep.zip --script tests\startup.txt

echo.
echo ========================================================
echo [DONE] Commands testing finished.
echo ========================================================
pause
