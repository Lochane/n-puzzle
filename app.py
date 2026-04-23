import PySimpleGUI as sg
from file import File, format_error
import random
from solver import solve

MAX_SIZE = 20

class Application:
    def __init__(self):
        self.file = None
        self.window = self._create_window()

    def _create_window(self, matrix=None):
        n = len(matrix) if matrix else 0

        grid = [
            [sg.Input(
                str(matrix[r][c]) if matrix[r][c] != 0 else "",
                justification="center",
                size=(3, 2),
                font=("Helvetica", 20),
                key=(r, c),
                disabled=True,
                use_readonly_for_disable=True
            )
            for c in range(n)]
            for r in range(n)
        ] if matrix else []

        grid_height = max(n * 3, 10) 

        layout = [
            [sg.Menu([["File", ["Open", "Save", "Save As", "Generate", "Exit"]]])],
            [
                sg.Column(grid, vertical_alignment="top"),
                sg.VSeparator(),
                sg.Multiline(
                    size=(60, grid_height),
                    key="-OUT-",
                    reroute_stdout=True,
                    write_only=True,
                    autoscroll=True,
                    disabled=True,
                    text_color="white",
                    background_color="darkblue"
                )
            ],
            [sg.Button("Solve", key="-SOLVE-")]
        ]

        return sg.Window("n-puzzle", layout, resizable=False, finalize=True)

    def _update_grid(self, matrix):
        self.window.close()
        self.window = self._create_window(matrix)
    def _clear_grid(self):
        self.file = None
        self.window.close()
        self.window = self._create_window()
    def run(self):
        while True:
            event, values = self.window.read()

            if event in (sg.WIN_CLOSED, "Exit"):
                break

            if event == "Open":
                self._open_file()

            elif event == "Generate":
                self._generate_matrix()

            elif event == "Save":
                self._save_file(values)

            elif event == "Save As":
                self._save_file_as(values)

            elif event == "-SOLVE-":
                if self.file:
                    n = self.file.matrix_size
                    matrix = self.file.matrix
                    solve(matrix)
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