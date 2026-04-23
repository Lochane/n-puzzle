import PySimpleGUI as sg
from file import File, format_error


class Application:
    def __init__(self):
        self.file = None
        self.window = self._create_window()

    def _create_window(self):
        layout = [
            [sg.Menu([["File", ["Open", "Save", "Save As", "Exit"]]])],
            [sg.Multiline("", key="-TEXT-", size=(30, 15), disabled=True)]
        ]
        return sg.Window("n-puzzle", layout, resizable=True)

    def run(self):
        while True:
            event, values = self.window.read()

            if event in (sg.WIN_CLOSED, "Exit"):
                break

            if event == "Open":
                self._open_file()

            elif event == "Save":
                self._save_file(values)

            elif event == "Save As":
                self._save_file_as(values)

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
            self.window["-TEXT-"].update(self.file.content)

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