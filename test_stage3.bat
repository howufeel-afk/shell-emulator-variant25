@echo off
echo ========================================================
echo [TEST STAGE 3] VFS loading and error handling
echo ========================================================

echo.
echo Generating VFS archives...
py tests\generate_vfs.py

echo.
echo [1/4] Test minimal VFS (1 file in root):
echo vfs-info & echo ls & echo exit | py src\main.py --vfs tests\vfs_minimal.zip

echo.
echo [2/4] Test deep VFS (more than 3 levels):
echo vfs-info & echo ls home/user/projects/code & echo exit | py src\main.py --vfs tests\vfs_deep.zip

echo.
echo [3/4] Test error: nonexistent VFS file:
echo exit | py src\main.py --vfs tests\missing_archive.zip

echo.
echo [4/4] Test error: corrupted archive:
echo corrupted_data > tests\bad_format.zip
echo exit | py src\main.py --vfs tests\bad_format.zip
del tests\bad_format.zip

echo.
echo ========================================================
echo [DONE] Stage 3 testing finished.
echo ========================================================
pause
