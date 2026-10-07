"""Скрипт создания тестовых архивов VFS."""

import zipfile


def make_archives() -> None:
    """Сгенерировать минимальный и глубоко вложенный архивы VFS."""
    with zipfile.ZipFile("tests/vfs_minimal.zip", "w") as arch:
        arch.writestr("readme.txt", "Minimal root file\n")

    with zipfile.ZipFile("tests/vfs_deep.zip", "w") as arch:
        arch.writestr("var/log/syslog", "Oct 07 system boot ok\n" * 15)
        arch.writestr(
            "home/user/projects/code/main.c",
            "#include <stdio.h>\nint main() { return 0; }\n",
        )
        arch.writestr(
            "home/user/notes.txt",
            "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n",
        )
        arch.writestr("etc/config.json", '{"version": 1.0}\n')


if __name__ == "__main__":
    make_archives()
