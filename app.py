import PySimpleGUI as sg
from file import File, format_error
import random
from solver import solve

class Application:
    def __init__(self):
        self.file = None
        self.window = self._create_window()

    def _create_window(self):
        layout = [
            [sg.Menu([["File", ["Open", "Save", "Save As", "Generate", "Exit"]]])],

            [sg.Multiline("", key="-TEXT-", size=(30, 15), disabled=True)],

            [sg.Button("Solve", key="-SOLVE-")]
        ]
        return sg.Window("n-puzzle", layout, resizable=True)

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
            self.window["-TEXT-"].update(format_matrix(self.file.matrix))

        except Exception as e:
            sg.popup_error(format_error(str(e)))

    def _save_file(self, values):
        if not self.file:
            sg.popup("No file open. Use Save As.")
            return

        try:
            self.file.content = values["-TEXT-"]
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
            self.file.content = values["-TEXT-"]
            self.file.save()
            sg.popup("File saved.")
        except Exception as e:
            sg.popup_error(format_error(str(e)))

    def _generate_matrix(self):
        n = sg.popup_get_text("Matrix size (n x n):", default_text="3")

        if not n:
            return

        try:
            n = int(n)
            if n <= 0:
                raise ValueError()

        except ValueError:
            sg.popup_error("Invalid size")
            return

        # generate a shuffled valid permutation
        values = list(range(n * n))
        random.shuffle(values)

        matrix = [
            values[i * n:(i + 1) * n]
            for i in range(n)
        ]

        # wrap into File object (so solver still works)
        self.file = File.__new__(File)  # bypass constructor
        self.file._file_path = None
        self.file._content = ""
        self.file._matrix_size = n
        self.file._matrix = matrix

        self.window["-TEXT-"].update(format_matrix(matrix))
def format_matrix(matrix):
    return "\n".join(" ".join(map(str, row)) for row in matrix)