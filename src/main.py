"""Главный модуль эмулятора оболочки UNIX (Вариант №25)."""

import argparse
import getpass
import os
import shlex
import socket
import sys
import time

from vfs import BYTES_PER_KB, InMemoryVFS

DEFAULT_HEAD_LINES = 10
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 3600


class Emulator:

    def __init__(self, vfs_path=None, prompt=None, script=None) -> None:
        self.vfs_path = vfs_path
        self.script_path = script
        self.start_time = time.time()
        self.cwd = "/"

        user = getpass.getuser()
        host = socket.gethostname()
        self.prompt = prompt if prompt else f"{user}@{host}:~$ "

        self.print_debug()
        self.vfs = InMemoryVFS()
        self._load_initial_vfs()

    def _load_initial_vfs(self) -> None:
        if not self.vfs_path:
            return
        try:
            self.vfs.load_zip(self.vfs_path)
        except (FileNotFoundError, ValueError) as err:
            print(f"Ошибка загрузки VFS: {err}", file=sys.stderr)

    def print_debug(self) -> None:
        print("=== Параметры конфигурации эмулятора ===")
        print(f"VFS path:       {self.vfs_path}")
        print(f"Custom prompt:  {self.prompt}")
        print(f"Startup script: {self.script_path}")
        print("=========================================")

    def execute_line(self, line: str) -> bool:
        clean = line.strip()
        if not clean or clean.startswith("#"):
            return True
        try:
            tokens = shlex.split(clean)
        except ValueError as err:
            print(f"Ошибка синтаксиса: {err}", file=sys.stderr)
            return True
        cmd, *args = tokens
        return self.dispatch(cmd, args)

    def dispatch(self, cmd: str, args: list) -> bool:
        handlers = {
            "exit": lambda _: False,
            "vfs-info": self.cmd_vfs_info,
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "head": self.cmd_head,
            "du": self.cmd_du,
            "uptime": self.cmd_uptime,
            "mv": self.cmd_mv,
        }
        if cmd not in handlers:
            print(f"{cmd}: команда не найдена", file=sys.stderr)
            return True
        res = handlers[cmd](args)
        return True if res is None else res

    def cmd_vfs_info(self, _args: list) -> None:
        if not self.vfs.vfs_name:
            print("VFS не подключена.")
            return
        print(f"Имя VFS: {self.vfs.vfs_name}")
        print(f"SHA-256: {self.vfs.vfs_hash}")

    def cmd_ls(self, args: list) -> None:
        target = args[0] if args else "."
        path = self.vfs.resolve(self.cwd, target)
        if not self.vfs.exists(path):
            print(f"ls: '{target}': Нет такого файла", file=sys.stderr)
            return
        if self.vfs.is_dir(path):
            items = self.vfs.list_dir(path)
            if items:
                print("  ".join(items))
        else:
            print(os.path.basename(path))

    def cmd_cd(self, args: list) -> None:
        target = args[0] if args else "/"
        path = self.vfs.resolve(self.cwd, target)
        if not self.vfs.exists(path):
            print(f"cd: {target}: Нет такого каталога", file=sys.stderr)
        elif not self.vfs.is_dir(path):
            print(f"cd: {target}: Не является каталогом", file=sys.stderr)
        else:
            self.cwd = path

    def cmd_head(self, args: list) -> None:
        count, filename = self._parse_head_args(args)
        if not filename:
            print("head: пропущен операнд", file=sys.stderr)
            return
        path = self.vfs.resolve(self.cwd, filename)
        if not self.vfs.exists(path) or self.vfs.is_dir(path):
            print(f"head: ошибка чтения '{filename}'", file=sys.stderr)
            return
        raw = self.vfs.fs[path]["data"]
        text = raw.decode("utf-8", errors="replace")
        for line in text.splitlines()[:count]:
            print(line)

    def _parse_head_args(self, args: list) -> tuple:
        count = DEFAULT_HEAD_LINES
        filename = None
        idx = 0
        while idx < len(args):
            if args[idx] == "-n" and idx + 1 < len(args):
                if args[idx + 1].isdigit():
                    count = int(args[idx + 1])
                    idx += 2
                    continue
            filename = args[idx]
            idx += 1
        return count, filename

    def cmd_du(self, args: list) -> None:
        target = args[0] if args else "."
        path = self.vfs.resolve(self.cwd, target)
        if not self.vfs.exists(path):
            print(f"du: '{target}': Файл не найден", file=sys.stderr)
            return
        prefix = "" if path == "/" else path
        if self.vfs.is_dir(path):
            dirs = []
            for k in self.vfs.fs:
                if self.vfs.is_dir(k):
                    if k == path or k.startswith(prefix + "/"):
                        dirs.append(k)
            for dir_path in sorted(dirs):
                raw_sz = self.vfs.get_size(dir_path)
                kb = (raw_sz + BYTES_PER_KB - 1) // BYTES_PER_KB
                is_cwd = dir_path == self.cwd
                rel = "." if is_cwd else os.path.relpath(dir_path, self.cwd)
                print(f"{kb}\t{rel}")
        else:
            kb = (self.vfs.get_size(path) + BYTES_PER_KB - 1) // BYTES_PER_KB
            print(f"{kb}\t{target}")

    def cmd_uptime(self, _args: list) -> None:
        sec = int(time.time() - self.start_time)
        hrs = sec // SECONDS_IN_HOUR
        mins = (sec % SECONDS_IN_HOUR) // SECONDS_IN_MINUTE
        rem = sec % SECONDS_IN_MINUTE
        print(f"up {hrs:02d}:{mins:02d}:{rem:02d}")

    def cmd_mv(self, args: list) -> None:
        if len(args) < 2:
            print("mv: пропущен операнд", file=sys.stderr)
            return
        src = self.vfs.resolve(self.cwd, args[0])
        dst = self.vfs.resolve(self.cwd, args[1])
        try:
            self.vfs.move(src, dst)
        except FileNotFoundError as err:
            print(f"{err}", file=sys.stderr)

    def run_script(self, script_path: str) -> None:
        if not os.path.exists(script_path):
            print(f"Скрипт '{script_path}' не найден", file=sys.stderr)
            return
        with open(script_path, "r", encoding="utf-8") as script_file:
            for raw_line in script_file:
                clean = raw_line.rstrip("\r\n")
                print(f"{self.prompt}{clean}")
                if not self.execute_line(clean):
                    break

    def run_repl(self) -> None:
        while True:
            try:
                line = input(self.prompt)
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not self.execute_line(line):
                break

    def run(self) -> None:
        if self.script_path:
            self.run_script(self.script_path)
        else:
            self.run_repl()


def main() -> None:
    parser = argparse.ArgumentParser(description="UNIX Shell Emulator")
    parser.add_argument("--vfs", help="Путь к VFS архиву (ZIP)")
    parser.add_argument("--prompt", help="Пользовательское приглашение")
    parser.add_argument("--script", help="Путь к стартовому скрипту")
    args = parser.parse_args()

    app = Emulator(vfs_path=args.vfs, prompt=args.prompt, script=args.script)
    app.run()


if __name__ == "__main__":
    main()
