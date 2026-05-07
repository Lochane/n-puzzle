import PySimpleGUI as sg
from file import File, format_error
import random
import numpy as np
import threading
from algo import Solver

MAX_SIZE = 8
PLAYBACK_MIN_MS = 10
PLAYBACK_MAX_MS = 200
PLAYBACK_SPEED_SCALE = 200  # move count at which max speed is reached
class Application:

    # ==========================INIT==========================

    def __init__(self):
        default_matrix = [[0] * 3 for _ in range(3)]
        self.file = File.__new__(File)
        self.file._file_path = None
        self.file._content = ""
        self.file._matrix_size = 3
        self.file._matrix = default_matrix
        self.algo = Solver()
        self.curr_path = None
        self.playing = False
        self.goal = None
        self.window = self._create_window(default_matrix)

    def _create_window(self, matrix=None, location=(0, 0)):
        title = "n-puzzle"
        if self.file and self.file._file_path:
            title = f"n-puzzle — {self.file._file_path}"
        n = len(matrix) if matrix else 3

        size_row = [
            sg.Input(
                str(n),
                justification="center",
                size=(3, 1),
                font=("Courier New", 14),
                key="size",
            ),
            sg.Button("Resize", key="-RESIZE-", font=("Helvetica", 10))
        ]

        grid = [
            [sg.pin(sg.Input(
                str(matrix[r][c]) if (matrix and r < len(matrix) and c < len(matrix[r]) and matrix[r][c] != 0) else "",
                justification="center",
                size=(3, 1),
                font=("Courier New", 14),
                key=(r, c),
                visible=(r < n and c < n),
            ))
            for c in range(MAX_SIZE)]
            for r in range(MAX_SIZE)
        ]

        timeline = [
            sg.pin(sg.Column([
                [sg.Column([
                    [sg.Slider(
                        range=(0, 0),
                        default_value=0,
                        orientation='h',
                        size=(40, 15),
                        key='-SLIDER-',
                        enable_events=True,
                        expand_x=True,
                    )],
                ], expand_x=True, pad=(5, 0))],
                [
                    sg.Button("⏮", key="-REWIND-",     font=("Helvetica", 12)),
                    sg.Button("⏪", key="-STEP-BACK-",  font=("Helvetica", 12)),
                    sg.Button("▶", key="-PLAY-PAUSE-", font=("Helvetica", 12)),
                    sg.Button("⏩", key="-STEP-FWD-",   font=("Helvetica", 12)),
                    sg.Button("⏭", key="-END-",         font=("Helvetica", 12)),
                    sg.Text("0 / 0", key="-STEP-LABEL-", font=("Courier New", 11)),
                ],
            ], key='-TIMELINE-', visible=False, expand_x=True))
        ]

        full_grid = [size_row] + grid + [timeline]

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
            [sg.Button("Generate", key="-GENERATE-"), sg.Checkbox("Solvable only", default=True, key="-SOLVABLE-"), sg.Button("Solve", key="-SOLVE-")],
            [sg.pin(sg.Column([[sg.Text("Algorithm", size=(8, 1)), sg.OptionMenu(['A*', 'greedy_A*', 'uniform'], default_value='A*', key='-ALGO-', enable_events=True)]], key='-ALGO-ROW-'))],
            [sg.pin(sg.Column([[sg.Text("Heuristic", size=(8, 1)), sg.OptionMenu(['manhattan', 'linear_conflict', 'hamming'], default_value='manhattan', key='-HEURISTIC-')]], key='-HEURISTIC-ROW-'))],
            [sg.pin(sg.Column([
                [sg.ProgressBar(max_value=100, size=(30, 10), key='-PROGRESS-', expand_x=True)]
            ], key='-PROGRESS-ROW-', visible=False, expand_x=True))],
        ]

        win = sg.Window(title, layout, finalize=True, location=location, resizable=True)
        win['-PROGRESS-'].Widget.config(mode='indeterminate')
        return win
    def _log(self, message, color="blue4"):
        out = self.window["-OUT-"]
        out.reroute_stdout = False
        out.update(disabled=False)
        out.print(message, text_color=color)
        out.update(disabled=True)
        out.reroute_stdout = True

    # ==========================GRID==========================

    def _apply_grid_visibility(self, n):
        for r in range(MAX_SIZE):
            for c in range(MAX_SIZE):
                self.window[(r, c)].update(visible=(r < n and c < n))

    def _refresh_grid(self, matrix):
        n = len(matrix)
        for r in range(n):
            for c in range(n):
                val = matrix[r][c]
                self.window[(r, c)].update(str(val) if val != 0 else "")
        self._highlight_grid(matrix)

    def _highlight_grid(self, matrix):
        n = len(matrix)
        for r in range(n):
            for c in range(n):
                val = matrix[r][c]
                if self.goal and val != 0 and val == self.goal[r][c]:
                    bg = "pale green"
                else:
                    bg = "white"
                self.window[(r, c)].update(background_color=bg)

    def _update_grid(self, matrix):
        n = len(matrix)
        self.file._matrix_size = n
        self._apply_grid_visibility(n)
        self._refresh_grid(matrix)
        self.window["size"].update(str(n))

    def _resize_grid(self, values):
        try:
            n = int(values["size"])
            if n <= 0 or n > MAX_SIZE:
                raise ValueError()
        except (ValueError, KeyError):
            sg.popup_error("Invalid size")
            return

        old = self.file._matrix
        old_n = self.file._matrix_size

        matrix = [[0] * n for _ in range(n)]
        for r in range(min(n, old_n)):
            for c in range(min(n, old_n)):
                matrix[r][c] = old[r][c]

        self.file._matrix_size = n
        self.file._matrix = matrix
        self.goal = None

        self._apply_grid_visibility(n)
        self._refresh_grid(matrix)

    def _clear_grid(self):
        default_matrix = [[0] * 3 for _ in range(3)]
        self.file = File.__new__(File)
        self.file._file_path = None
        self.file._content = ""
        self.file._matrix_size = 3
        self.file._matrix = default_matrix
        self._update_grid(default_matrix)

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
        return None

    def _generate_matrix(self, solvable=True):
        self.goal = None
        self.curr_path = None
        self.playing = False
        self.window['-PLAY-PAUSE-'].update("▶")
        self.window['-TIMELINE-'].update(visible=False)
        n = self.file._matrix_size

        if solvable:
            solver = Solver()
            solver.N = n
            matrix = solver.snail_solution().tolist()
            pos = next((r, c) for r in range(n) for c in range(n) if matrix[r][c] == 0)
            moves = n * n * 20
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for _ in range(moves):
                r, c = pos
                random.shuffle(directions)
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < n:
                        matrix[r][c], matrix[nr][nc] = matrix[nr][nc], matrix[r][c]
                        pos = (nr, nc)
                        break
        else:
            values = list(range(n * n))
            random.shuffle(values)
            matrix = [values[i * n:(i + 1) * n] for i in range(n)]

        self.file._matrix = matrix
        self._refresh_grid(matrix)

    #==========================PLAYBACK==========================


    def _playback_timeout(self):
        if not self.curr_path:
            return PLAYBACK_MAX_MS
        steps = len(self.curr_path) - 1
        t = PLAYBACK_MAX_MS - (steps / PLAYBACK_SPEED_SCALE) * (PLAYBACK_MAX_MS - PLAYBACK_MIN_MS)
        return max(PLAYBACK_MIN_MS, min(PLAYBACK_MAX_MS, int(t)))

    def _playback_goto(self, step):
        steps = len(self.curr_path) - 1
        step = max(0, min(steps, step))
        self.window['-SLIDER-'].update(value=step)
        self.window['-STEP-LABEL-'].update(f"{step} / {steps}")
        self._refresh_grid(self.curr_path[step].tolist())

    #==========================PARSING==========================

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
    # ==========================SOLVER THREAD==========================

    def _solve_thread(self, matrix, algorithm, heuristic):
        result = self.algo.run(matrix, algorithm=algorithm, heuristic=heuristic)
        self.window.write_event_value('-SOLVE-DONE-', result)
    # ==========================MAIN LOOP==========================

    def run(self):
        self._generate_matrix()
        while True:
            timeout = self._playback_timeout() if self.playing else None
            event, values = self.window.read(timeout=timeout)

            if event in (sg.WIN_CLOSED, "Exit"):
                break

            # file menu
            elif event == "Open":
                self._open_file()
            elif event == "Save":
                self._read_matrix_from_grid()
                self._save_file(values)
            elif event == "Save As":
                self._read_matrix_from_grid()
                self._save_file_as(values)

            # grid
            elif event == "-GENERATE-":
                self._generate_matrix(solvable=values["-SOLVABLE-"])
            elif event == "-RESIZE-":
                self._resize_grid(values)

            # solver
            elif event == '-ALGO-':
                is_uniform = values['-ALGO-'] == 'uniform'
                self.window['-HEURISTIC-ROW-'].update(visible=not is_uniform)
            elif event == "-SOLVE-":
                if self.file:
                    self._read_matrix_from_grid()
                    error = self._validate_matrix()
                    if error:
                        self._log(f"Invalid matrix: {error}", color="red")
                    else:
                        self._log("Solving...", color="green")
                        algorithm = values['-ALGO-']
                        heuristic = values['-HEURISTIC-']
                        self.window['-PROGRESS-ROW-'].update(visible=True)
                        self.window['-PROGRESS-'].Widget.start(12)
                        self.window['-SOLVE-'].update(disabled=True)
                        threading.Thread(
                            target=self._solve_thread,
                            args=(np.array(self.file._matrix), algorithm, heuristic),
                            daemon=True
                        ).start()
                else:
                    self._log("No file loaded", color="orange")

            elif event == '-SOLVE-DONE-':
                self.window['-PROGRESS-'].Widget.stop()
                self.window['-PROGRESS-ROW-'].update(visible=False)
                self.window['-SOLVE-'].update(disabled=False)
                result = values['-SOLVE-DONE-']
                if result:
                    self.curr_path = result['path']
                    steps = result['nb_moves']
                    self._log(f"Solved in {steps} moves ({result['count_node']} nodes explored, {result['max_node']} max in memory)", color="green")
                    self.goal = self.algo.goal.tolist()
                    self.playing = False
                    self.window['-PLAY-PAUSE-'].update("▶")
                    self.window['-SLIDER-'].update(range=(0, steps), value=0)
                    self.window['-STEP-LABEL-'].update(f"0 / {steps}")
                    self.window['-TIMELINE-'].update(visible=True)
                    self._refresh_grid(self.curr_path[0].tolist())
                else:
                    self._log("No solution found.", color="red")

            # playback
            elif event == '-SLIDER-':
                self._playback_goto(int(values['-SLIDER-']))
            elif event == '-REWIND-':
                self._playback_goto(0)
            elif event == '-END-':
                self._playback_goto(len(self.curr_path) - 1)
            elif event == '-STEP-BACK-':
                self._playback_goto(int(values['-SLIDER-']) - 1)
            elif event == '-STEP-FWD-':
                self._playback_goto(int(values['-SLIDER-']) + 1)
            elif event == '-PLAY-PAUSE-':
                self.playing = not self.playing
                self.window['-PLAY-PAUSE-'].update("⏸" if self.playing else "▶")
            elif event == sg.TIMEOUT_EVENT:
                if self.playing and self.curr_path:
                    step = int(values['-SLIDER-']) + 1
                    if step > len(self.curr_path) - 1:
                        self.playing = False
                        self.window['-PLAY-PAUSE-'].update("▶")
                    else:
                        self._playback_goto(step)

        self.window.close()