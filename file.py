from pathlib import Path


def format_error(msg: str) -> str:
    return f"n-puzzle: error: {msg.strip().lower()}"


class File:
    def __init__(self, file_path: str):
        self._file_path = Path(file_path)
        self._content = ""
        self._matrix_size = None
        self._matrix = None
        self._validate_file()

    def _validate_file(self):
        if self._file_path.suffix != ".txt":
            raise ValueError(f"'{self._file_path.name}' is not a .txt file.")

    def load(self):
        with open(self._file_path, "r", encoding="utf-8") as file:
            self._content = file.read()

        self._parse()

    def save(self, new_path: str = None):
        path = Path(new_path) if new_path else self._file_path
        with open(path, "w", encoding="utf-8") as file:
            file.write(self._content)

    # ---------- parser ---------- #

    def _parse(self):
        lines = self._content.splitlines()

        cleaned = []
        for line in lines:
            line = line.split("#", 1)[0].strip()
            if line:
                cleaned.append(line)

        if not cleaned:
            raise ValueError("Empty input")

        try:
            n = int(cleaned[0])
        except ValueError:
            raise ValueError("First line must be an integer matrix size")

        if n <= 0:
            raise ValueError("Matrix size must be positive")

        rows = cleaned[1:]

        if len(rows) < n:
            raise ValueError(f"Expected {n} rows, got {len(rows)}")

        if len(rows) > n:
            raise ValueError("Too many rows for declared matrix size")

        matrix = []

        for i, line in enumerate(rows, start=1):
            parts = line.split()

            if len(parts) != n:
                raise ValueError(f"Row {i} must have exactly {n} elements")

            try:
                matrix.append([int(x) for x in parts])
            except ValueError:
                raise ValueError(f"Row {i} contains non-integer values")

        self._matrix_size = n
        self._matrix = matrix