#!/bin/bash
set -e

python3 tests/generate_vfs.py

echo "=== Запуск тестов проекта ==="
python3 -m unittest discover -s tests -v

echo "=== Демонстрация работы эмулятора по сценарию ==="
python3 src/main.py --vfs tests/vfs_deep.zip --prompt "shell$ " --script tests/startup.txt
