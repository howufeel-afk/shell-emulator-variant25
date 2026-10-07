"""Модуль виртуальной файловой системы (VFS) в оперативной памяти."""

import hashlib
import os
import zipfile

BYTES_PER_KB = 1024
DEFAULT_DIR_SIZE = 4096


class InMemoryVFS:
    """Виртуальная файловая система, работающая в оперативной памяти."""

    def __init__(self, zip_path: str = None) -> None:
        """Инициализировать VFS и загрузить архив при наличии."""
        self.fs = {"/": {"type": "dir"}}
        self.vfs_name = ""
        self.vfs_hash = ""
        if zip_path:
            self.load_zip(zip_path)

    def load_zip(self, zip_path: str) -> None:
        """Загрузить структуру файлов и директорий из ZIP-архива."""
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Файл VFS не найден: {zip_path}")
        if not zipfile.is_zipfile(zip_path):
            raise ValueError(f"Неверный формат VFS: {zip_path}")

        with open(zip_path, "rb") as archive_file:
            data = archive_file.read()
            self.vfs_hash = hashlib.sha256(data).hexdigest()
        self.vfs_name = os.path.basename(zip_path)

        with zipfile.ZipFile(zip_path, "r") as archive:
            for item in archive.infolist():
                norm = "/" + item.filename.strip("/")
                if item.is_dir():
                    self._ensure_dir(norm)
                else:
                    self._ensure_dir(os.path.dirname(norm))
                    raw_bytes = archive.read(item.filename)
                    self.fs[norm] = {
                        "type": "file",
                        "data": bytearray(raw_bytes),
                    }

    def _ensure_dir(self, path: str) -> None:
        """Рекурсивно создать промежуточные директории."""
        if not path or path == "/":
            return
        parts = [p for p in path.split("/") if p]
        curr = ""
        for seg in parts:
            curr += "/" + seg
            if curr not in self.fs:
                self.fs[curr] = {"type": "dir"}

    def resolve(self, cwd: str, target: str) -> str:
        """Преобразовать относительный путь в абсолютный."""
        if not target:
            return cwd
        if target.startswith("/"):
            raw = target
        else:
            base = "" if cwd == "/" else cwd
            raw = f"{base}/{target}"

        parts = []
        for segment in raw.split("/"):
            if not segment or segment == ".":
                continue
            if segment == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(segment)
        return "/" + "/".join(parts)

    def exists(self, path: str) -> bool:
        """Проверить существование узла в виртуальной системе."""
        return path in self.fs

    def is_dir(self, path: str) -> bool:
        """Проверить, является ли узел каталогом."""
        return self.fs.get(path, {}).get("type") == "dir"

    def list_dir(self, path: str) -> list:
        """Получить отсортированный список прямых потомков каталога."""
        prefix = "" if path == "/" else path
        items = set()
        for key in self.fs:
            if key != path and key.startswith(prefix + "/"):
                rel = key[len(prefix) + 1:]
                items.add(rel.split("/")[0])
        return sorted(list(items))

    def get_size(self, path: str) -> int:
        """Рассчитать суммарный размер файла или каталога в байтах."""
        if not self.exists(path):
            return 0
        if self.fs[path]["type"] == "file":
            return len(self.fs[path]["data"])
        total = DEFAULT_DIR_SIZE
        prefix = "" if path == "/" else path
        for key, val in self.fs.items():
            if key != path and key.startswith(prefix + "/"):
                if val["type"] == "file":
                    total += len(val["data"])
                else:
                    total += DEFAULT_DIR_SIZE
        return total

    def move(self, src: str, dst: str) -> None:
        """Переместить или переименовать файл/папку в ОЗУ."""
        if not self.exists(src):
            raise FileNotFoundError(f"mv: путь '{src}' не найден")
        if self.exists(dst) and self.is_dir(dst):
            base_name = os.path.basename(src.rstrip("/"))
            base_dst = "" if dst == "/" else dst
            final_dst = f"{base_dst}/{base_name}"
        else:
            parent = os.path.dirname(dst.rstrip("/"))
            if parent and not self.exists(parent):
                raise FileNotFoundError("mv: целевой каталог не существует")
            final_dst = dst.rstrip("/")

        to_rename = {}
        for key in list(self.fs.keys()):
            if key == src or key.startswith(src + "/"):
                to_rename[key] = final_dst + key[len(src):]

        for old_k, new_k in to_rename.items():
            self.fs[new_k] = self.fs.pop(old_k)
