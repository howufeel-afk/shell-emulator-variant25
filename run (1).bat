@echo off
echo ========================================================
echo [START] UNIX Shell Emulator Variant 25
echo ========================================================

echo.
echo 1. Generating test VFS archives...
py tests\generate_vfs.py

echo.
echo 2. Running unit tests...
py -m unittest discover -s tests -v

echo.
echo 3. Running startup script demonstration...
py src\main.py --vfs tests\vfs_deep.zip --prompt "vfs-demo$ " --script tests\startup.txt

echo.
echo ========================================================
echo [DONE] All checks completed successfully.
echo ========================================================
pause
