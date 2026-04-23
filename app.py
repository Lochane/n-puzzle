import PySimpleGUI as sg
from file import File, format_error
import random
from solver import solve

MAX_SIZE = 20

class Application:
    def __init__(self):
        self.file = None
        default_matrix = [[0] * 3 for _ in range(3)]
        self.window = self._create_window(default_matrix)

    def _create_window(self, matrix=None, location=(0, 0)):
        n = len(matrix) if matrix else 0

        size_row = [
            sg.Input(
                str(n) if n else "",
                justification="center",
                size=(3, 1),
                font=("Helvetica", 18),
                key="size",
            ),
            sg.Button("Resize", key="-RESIZE-", font=("Helvetica", 12))
        ] if matrix else []

        grid = [
            [sg.Input(
                str(matrix[r][c]) if matrix[r][c] != 0 else "",
                justification="center",
                size=(3, 1),
                font=("Helvetica", 18),
                key=(r, c),
            )
            for c in range(n)]
            for r in range(n)
        ] if matrix else []

        full_grid = ([size_row] + grid) if matrix else []

        layout = [
            [sg.Menu([["File", ["Open", "Save", "Save As", "Generate", "Exit"]]])],
            [
                sg.Column(full_grid, vertical_alignment="top"),
                sg.VSeparator(),
                sg.Multiline(
                    size=(25, 50),
                    key="-OUT-",
                    reroute_stdout=True,
                    write_only=True,
                    autoscroll=True,
                    disabled=True,
                    text_color="white",
                    background_color="darkblue"
                ),
            ],
            [sg.Button("Solve", key="-SOLVE-")]
        ]

        return sg.Window("n-puzzle", layout, resizable=False, finalize=True, location=location)

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
                    row.append(0)
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
        self.file = None
        location = self.window.current_location()
        self.window.close()
        default_matrix = [[0] * 3 for _ in range(3)]
        self.window = self._create_window(default_matrix)

    def run(self):
        while True:
            event, values = self.window.read()

            if event in (sg.WIN_CLOSED, "Exit"):
                break

            if event == "Open":
                self._open_file()

            elif event == "Generate":
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
                    solve(self.file._matrix)
                else:
                    sg.popup("No file loaded")

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
            self.file = File(path)
            self.file.save()
            sg.popup("File saved.")
        except Exception as e:
            sg.popup_error(format_error(str(e)))

    def _generate_matrix(self):
        n = sg.popup_get_text("Matrix size (n x n), maximum size of " + str(MAX_SIZE), default_text="3")

        if not n:
            return

        try:
            n = int(n)
            if n <= 0:
                raise ValueError()
            if n > MAX_SIZE:
                raise ValueError()

        except ValueError:
            sg.popup_error("Invalid size")
            return

        values = list(range(n * n))
        random.shuffle(values)

        matrix = [
            values[i * n:(i + 1) * n]
            for i in range(n)
        ]

        self.file = File.__new__(File)
        self.file._file_path = None
        self.file._content = ""
        self.file._matrix_size = n
        self.file._matrix = matrix

        self._update_grid(matrix)