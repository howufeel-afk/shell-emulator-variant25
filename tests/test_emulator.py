"""Модульные тесты для эмулятора и VFS."""

import os
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from vfs import InMemoryVFS
from main import Emulator
from generate_vfs import make_archives


class TestVFS(unittest.TestCase):
    """Набор тестов виртуальной файловой системы."""

    @classmethod
    def setUpClass(cls) -> None:
        """Создать тестовые архивы."""
        make_archives()

    def test_vfs_loading(self) -> None:
        """Проверка загрузки архива и расчета SHA-256."""
        arch = "tests/vfs_minimal.zip" if os.path.exists("tests/vfs_minimal.zip") else "vfs_minimal.zip"
        vfs = InMemoryVFS(arch)
        self.assertTrue(vfs.vfs_name.endswith(".zip"))
        self.assertTrue(len(vfs.vfs_hash) == 64)
        self.assertTrue(vfs.exists("/readme.txt"))

    def test_vfs_deep_hierarchy(self) -> None:
        """Проверка глубины вложения более 3 уровней."""
        arch = "tests/vfs_deep.zip" if os.path.exists("tests/vfs_deep.zip") else "vfs_deep.zip"
        vfs = InMemoryVFS(arch)
        self.assertTrue(vfs.exists("/home/user/projects/code/main.c"))
        self.assertTrue(vfs.is_dir("/home/user/projects"))

    def test_vfs_move_in_memory(self) -> None:
        """Проверка перемещения/переименования файлов без диска."""
        arch = "tests/vfs_deep.zip" if os.path.exists("tests/vfs_deep.zip") else "vfs_deep.zip"
        vfs = InMemoryVFS(arch)
        vfs.move("/home/user/notes.txt", "/home/user/notes_new.txt")
        self.assertFalse(vfs.exists("/home/user/notes.txt"))
        self.assertTrue(vfs.exists("/home/user/notes_new.txt"))


class TestEmulatorCommands(unittest.TestCase):
    """Набор тестов команд эмулятора."""

    def setUp(self) -> None:
        """Инициализировать эмулятор с глубоким архивом."""
        arch = "tests/vfs_deep.zip" if os.path.exists("tests/vfs_deep.zip") else "vfs_deep.zip"
        self.emu = Emulator(vfs_path=arch, prompt="test$ ")

    def test_cd_and_pwd(self) -> None:
        """Проверка навигации cd."""
        self.emu.execute_line("cd home/user")
        self.assertEqual(self.emu.cwd, "/home/user")
        self.emu.execute_line("cd ..")
        self.assertEqual(self.emu.cwd, "/home")

    def test_unknown_command(self) -> None:
        """Проверка обработки неизвестной команды."""
        res = self.emu.execute_line("unknown_cmd_abc")
        self.assertTrue(res)


if __name__ == "__main__":
    unittest.main()
