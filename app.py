import PySimpleGUI as sg
from file import File, format_error
import random
import numpy as np
from solver import solve

MAX_SIZE = 20

class Application:
    def __init__(self):
        default_matrix = [[0] * 3 for _ in range(3)]
        self.file = File.__new__(File)
        self.file._file_path = None
        self.file._content = ""
        self.file._matrix_size = 3
        self.file._matrix = default_matrix
        self.window = self._create_window(default_matrix)

    def _create_window(self, matrix=None, location=(0, 0)):
        title = "n-puzzle"
        if self.file and self.file._file_path:
            title = f"n-puzzle — {self.file._file_path}"
        n = len(matrix) if matrix else 0

        size_row = [
            sg.Input(
                str(n) if n else "",
                justification="center",
                size=(3, 1),
                font=("Courier New", 14),
                key="size",
            ),
            sg.Button("Resize", key="-RESIZE-", font=("Helvetica", 10))
        ] if matrix else []

        grid = [
            [sg.Input(
                str(matrix[r][c]) if matrix[r][c] != 0 else "",
                justification="center",
                size=(3, 1),
                font=("Courier New", 14),
                key=(r, c),
            )
            for c in range(n)]
            for r in range(n)
        ] if matrix else []

        full_grid = ([size_row] + grid) if matrix else []

        layout = [
            [sg.Menu([["File", ["Open", "Save", "Save As", "Exit"]]])],
            [
                sg.Column(full_grid, vertical_alignment="top"),
                sg.VSeparator(),
                sg.Multiline(
                    size=(20, 20),
                    font=("Courier New", 12),
                    key="-OUT-",
                    autoscroll=True,
                    disabled=True,
                    reroute_stdout=True,
                    background_color="lightsteelblue",
                    expand_x=True,
                    expand_y=True,
                ),
            ],
            [sg.Button("Generate", key="-GENERATE-"), sg.Button("Solve", key="-SOLVE-")]
        ]
        win = sg.Window(title, layout, finalize=True, location=location, resizable=True)
        return win

    def _log(self, message, color="blue4"):
        out = self.window["-OUT-"]
        out.reroute_stdout = False
        out.update(disabled=False)
        out.print(message, text_color=color)
        out.update(disabled=True)
        out.reroute_stdout = True

    def _validate_matrix(self):
        matrix = self.file._matrix
        n = self.file._matrix_size
        expected = set(range(n * n))
        found = set()

        for r in range(n):
            for c in range(n):
                val = matrix[r][c]
                if not isinstance(val, int) or val < 0:
                    return f"Invalid value at ({r}, {c}): {val}"
                if val in found:
                    return f"Duplicate value: {val}"
                found.add(val)

        missing = expected - found
        if missing:
            return f"Missing values: {sorted(missing)}"

        return None  # all good
    def _read_matrix_from_grid(self):
        if not self.file:
            return
        n = self.file._matrix_size
        matrix = []
        for r in range(n):
            row = []
            for c in range(n):
                val = self.window[(r, c)].get().strip()
                try:
                    row.append(int(val) if val else 0)
                except ValueError:
                    row.append(val)
            matrix.append(row)
        self.file._matrix = matrix

    def _resize_grid(self, values):
        try:
            n = int(values["size"])
            if n <= 0 or n > MAX_SIZE:
                raise ValueError()
        except (ValueError, KeyError):
            sg.popup_error("Invalid size")
            return

        matrix = [[0] * n for _ in range(n)]

        if self.file:
            old = self.file._matrix
            old_n = self.file._matrix_size
            for r in range(min(n, old_n)):
                for c in range(min(n, old_n)):
                    matrix[r][c] = old[r][c]
            self.file._matrix_size = n
            self.file._matrix = matrix
        else:
            self.file = File.__new__(File)
            self.file._file_path = None
            self.file._content = ""
            self.file._matrix_size = n
            self.file._matrix = matrix

        x, y = self.window.current_location()
        self.window.close()
        self.window = self._create_window(matrix)

    def _update_grid(self, matrix):
        x, y = self.window.current_location()
        self.window.close()
        self.window = self._create_window(matrix)
    
    def _clear_grid(self):
        default_matrix = [[0] * 3 for _ in range(3)]
        self.file = File.__new__(File)
        self.file._file_path = None
        self.file._content = ""
        self.file._matrix_size = 3
        self.file._matrix = default_matrix
        x, y = self.window.current_location()
        self.window.close()
        self.window = self._create_window(default_matrix, location=(x, y - 30))

    def run(self):
        self._generate_matrix()
        while True:
            event, values = self.window.read()

            if event in (sg.WIN_CLOSED, "Exit"):
                break

            if event == "Open":
                self._open_file()

            elif event == "-GENERATE-":
                self._generate_matrix()

            elif event == "-RESIZE-":
                self._resize_grid(values)

            elif event == "Save":
                self._read_matrix_from_grid()
                self._save_file(values)

            elif event == "Save As":
                self._read_matrix_from_grid()
                self._save_file_as(values)

            elif event == "-SOLVE-":
                if self.file:
                    self._read_matrix_from_grid()
                    error = self._validate_matrix()
                    if error:
                        self._log(f"Invalid matrix: {error}", color="red")
                    else:
                        self._log("Solving...", color="green")
                        solve(np.array(self.file._matrix))
                else:
                    self._log("No file loaded", color="orange")

        self.window.close()

    def _open_file(self):
        win = sg.Window(
            "Open file",
            [[sg.Input(key="-FILE-"),
              sg.FileBrowse(file_types=(("Text Files", "*.txt"),))],
             [sg.OK(), sg.Cancel()]],
            modal=True
        )

        e, v = win.read()
        win.close()

        path = v["-FILE-"] if e == "OK" else None

        if not path:
            return

        try:
            self.file = File(path)
            self.file.load()
            self._update_grid(self.file.matrix)
        except Exception as e:
            sg.popup_error(format_error(str(e)))
            self._clear_grid()

    def _save_file(self, values):
        if not self.file:
            sg.popup("No file open. Use Save As.")
            return

        if not self.file._file_path:
            sg.popup("No file path set. Use Save As.")
            return

        try:
            self.file.save()
            sg.popup("File saved.")
        except Exception as e:
            sg.popup_error(format_error(str(e)))

    def _save_file_as(self, values):
        win = sg.Window(
            "Save file",
            [[sg.Input(key="-FILE-"),
            sg.FileSaveAs(file_types=(("Text Files", "*.txt"),))],
            [sg.OK(), sg.Cancel()]],
            modal=True
        )

        e, v = win.read()
        win.close()

        path = v["-FILE-"] if e == "OK" else None

        if not path:
            return

        try:
            self.file._file_path = path
            self.file.save()
            self.window.set_title(f"n-puzzle — {path}")
            sg.popup("File saved.")
        except Exception as e:
            sg.popup_error(format_error(str(e)))

    def _generate_matrix(self):
        n = self.file._matrix_size
        values = list(range(n * n))
        random.shuffle(values)

        matrix = [
            values[i * n:(i + 1) * n]
            for i in range(n)
        ]

        self.file._matrix = matrix

        for r in range(n):
            for c in range(n):
                val = matrix[r][c]
                self.window[(r, c)].update(str(val) if val != 0 else "")