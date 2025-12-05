import sys
import globals
from skull_finder import SkullFinder

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QPixmap, QFontDatabase, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QToolButton, QWidget, QGridLayout, QMessageBox, QLabel


class CellButton(QToolButton):

    def __init__(self, row: int, col: int, skull_finder: SkullFinder = None, window=None, parent=None):
        super().__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.row = row
        self.col = col
        self.skull_finder = skull_finder
        self.window = window
        self.setFixedSize(QSize(64, 64))
        self.setIconSize(QSize(64, 64))
        self.setDisabled(True)
        self.setCheckable(False)
        self.update_icon(globals.CELL_UNEXPLORED)
        self.clicked.connect(self.on_click)

    def get_coordinates(self):
        return self.row, self.col

    def update_icon(self, data: int):
        match data:
            case globals.CELL_EXPLORED_BLANK:
                self.setIcon(QPixmap("assets/cell-64x64-0.png"))
            case 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9:
                self.setIcon(QPixmap(f"assets/cell-64x64-{data}.png"))
            case globals.CELL_UNEXPLORED:
                self.setIcon(QPixmap("assets/cell-64x64-blank.png"))
            case globals.CELL_EXPLORED_SKULL:
                self.setIcon(QPixmap("assets/cell-64x64-skull.png"))
            case _:
                raise ValueError(f"Invalid data value: {data}")

    def on_click(self):
        print(f"Button Clicked: {self.get_coordinates()}")
        self.skull_finder.explore_cell(self.row, self.col)
        self.window.selected_row, self.window.selected_col = self.get_coordinates()
        self.window.update_button_grid(self.row, self.col)

        if self.skull_finder.status == globals.WIN:
            self.window.win()
        elif self.skull_finder.status == globals.LOSE:
            self.window.lose()


class GoalButton(QToolButton):

    def __init__(self, skull_finder: SkullFinder = None, window=None, parent=None):
        super().__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.skull_finder = skull_finder
        self.window = window
        self.setFixedSize(QSize(448, 64))
        self.setIconSize(QSize(448, 64))
        self.setDisabled(True)
        self.setCheckable(False)
        self.setIcon(QPixmap("assets/goal.png"))
        self.clicked.connect(self.on_click)

    def on_click(self):
        print(f"Button Clicked: Goal!")
        self.skull_finder.explore_cell(globals.ABOVE_TOP_ROW, -1)
        self.window.selected_row, self.window.selected_col = (globals.ABOVE_TOP_ROW, -1)
        self.window.disable_button_grid()
        self.window.win()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Skull Solver")
        # self.setFixedSize(QSize(500, 500))

        central = QWidget()
        self.layout = QGridLayout(central)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central)

        self.skull_finder = SkullFinder(row_size=7, col_size=7)
        self.skull_finder.fill_grid()
        self.selected_row = self.skull_finder.row_size
        self.selected_col = 0

        self.auto_grid = []
        for _ in range(self.skull_finder.row_size):
            row = [{"safe": False, "flag": False} for _ in range(self.skull_finder.col_size)]
            self.auto_grid.append(row)

        self.button_grid = []
        for row in range(0, self.skull_finder.row_size):
            button_row = []
            for col in range(0, self.skull_finder.col_size):
                button = CellButton(row=row, col=col, skull_finder=self.skull_finder, window=self)
                self.layout.addWidget(button, row + 1, col)
                button_row.append(button)

            self.button_grid.append(button_row)

        self.update_button_grid(self.selected_row, self.selected_col)

        self.auto_running = False
        self.option_auto = False
        self.button_auto = QToolButton()
        self.button_auto.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.button_auto.setText("Auto")
        self.button_auto.setCheckable(True)
        self.button_auto.setFixedSize(QSize(64, 64))
        self.button_auto.setIcon(QPixmap("assets/auto.png"))
        self.button_auto.setIconSize(QSize(32, 32))
        self.button_auto.clicked.connect(self.toggle_auto)
        self.layout.addWidget(self.button_auto, 8, 3)

        self.auto_timer = QTimer()
        self.auto_timer.setInterval(500)
        self.current_move_index = 0
        self.auto_timer.timeout.connect(self.auto_solve)

        self.button_goal = GoalButton(skull_finder=self.skull_finder, window=self)
        self.layout.addWidget(self.button_goal, 0, 0, 1, 7)

        self.destinations = []

        QFontDatabase.addApplicationFont("assets/vtRemingtonPortable.ttf")
        vt_remington = QFontDatabase.applicationFontFamilies(0)

        self.label_title_skull = QLabel("Skull")
        self.label_title_skull.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_title_solver = QLabel("Finder")
        self.label_title_solver.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_tutorial = QLabel("Use WASD or click red cells to move.\nCells show the number of adjacent skulls.\nAvoid skulls and reach the goal to win!")
        self.label_tutorial.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if vt_remington:
            self.label_title_skull.setFont(QFont(vt_remington[0], 32))
            self.label_title_solver.setFont(QFont(vt_remington[0], 32))
            self.label_tutorial.setFont(QFont(vt_remington[0], 12))

        self.label_title_skull.setStyleSheet("color: red;")
        self.label_title_solver.setStyleSheet("color: red;")
        self.layout.addWidget(self.label_title_skull, 8, 0, 1, 3)
        self.layout.addWidget(self.label_title_solver, 8, 4, 1, 3)

        self.layout.addWidget(self.label_tutorial, 9, 0, 1, 7)

    def toggle_auto(self):
        if not self.option_auto:
            self.option_auto = True
            self.button_auto.setChecked(True)
            self.auto_timer.start()
        else:
            self.button_auto.setChecked(False)
            self.button_auto.setDisabled(True)
            self.option_auto = False

    def update_button_grid(self, selected_row: int, selected_col: int, allow_diagonal: bool = False):
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                self.button_grid[row][col].update_icon(self.skull_finder.grid_displayed_data[row][col])
                self.button_grid[row][col].setDisabled(True)

        if selected_row == self.skull_finder.row_size:
            # Currently off the board, under the bottom row. Enable all bottom row cells
            for col in range(0, self.skull_finder.col_size):
                self.button_grid[selected_row - 1][col].setDisabled(False)

        else:
            # Currently on the board. Enable adjacent cells only. Diagonal cells are enabled if allow_diagonal is True
            for x in range(-1, 2):
                if not self.skull_finder.valid_row(selected_row + x):
                    continue

                for y in range(-1, 2):
                    if not self.skull_finder.valid_col(selected_col + y):
                        continue

                    if allow_diagonal is False and abs(x) == abs(y):
                        continue

                    self.button_grid[selected_row + x][selected_col + y].setDisabled(False)

            if selected_row == globals.TOP_ROW:
                self.button_goal.setDisabled(False)
            else:
                self.button_goal.setDisabled(True)

    def disable_button_grid(self):
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                self.button_grid[row][col].setDisabled(True)

    def keyPressEvent(self, event):
        match event.key():
            case Qt.Key.Key_A:
                # Currently off the board
                if not self.skull_finder.valid_row(self.selected_row):
                    return

                if self.skull_finder.valid_col(self.selected_col - 1):
                    self.button_grid[self.selected_row][self.selected_col - 1].on_click()

            case Qt.Key.Key_D:
                # Currently off the board
                if not self.skull_finder.valid_row(self.selected_row):
                    return

                if self.skull_finder.valid_col(self.selected_col + 1):
                    self.button_grid[self.selected_row][self.selected_col + 1].on_click()

            case Qt.Key.Key_W:
                # Currently off the board in the starting area, move to middle column
                if self.selected_row == self.skull_finder.row_size:
                    self.button_grid[self.selected_row - 1][self.skull_finder.col_size // 2].on_click()

                # Currently moving up from the top row to the goal
                elif self.selected_row == globals.TOP_ROW:
                    self.button_goal.on_click()

                # Elsewhere on the board
                elif self.skull_finder.valid_row(self.selected_row - 1):
                    self.button_grid[self.selected_row - 1][self.selected_col].on_click()

            case Qt.Key.Key_S:
                if self.skull_finder.valid_row(self.selected_row + 1):
                    self.button_grid[self.selected_row + 1][self.selected_col].on_click()
                else:
                    # Go off the board into the starting area
                    self.selected_row = self.skull_finder.row_size
                    self.update_button_grid(self.selected_row, self.selected_col)

    def win(self):
        self.skull_finder.reveal_all()
        self.update_button_grid(self.selected_row, self.selected_col)
        QMessageBox.information(self, "You Win!", "You Win!")
        self.restart()

    def lose(self):
        self.skull_finder.reveal_all()
        self.update_button_grid(self.selected_row, self.selected_col)
        QMessageBox.information(self, "You Lose!", "You Lose!")
        self.restart()

    def restart(self):
        self.option_auto = False
        self.auto_running = False
        self.button_auto.setChecked(False)
        self.button_auto.setDisabled(False)
        self.skull_finder = SkullFinder(row_size=7, col_size=7)
        self.skull_finder.fill_grid()
        self.skull_finder.status = globals.PLAYING
        self.selected_row = self.skull_finder.row_size
        self.selected_col = 0
        self.destinations = []

        self.auto_grid = []
        for _ in range(self.skull_finder.row_size):
            row = [{"safe": False, "flag": False} for _ in range(self.skull_finder.col_size)]
            self.auto_grid.append(row)

        # Replace the completed connected skull finder object with the new one for each button
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                self.button_grid[row][col].skull_finder = self.skull_finder

        self.update_button_grid(self.selected_row, self.selected_col)

    def auto_solve(self):
        self.auto_running = True
        self.destinations = self.analyze_board_simple()
        # Later loops can enable earlier loops to find new destinations. Check again
        if not self.destinations:
            self.destinations = self.analyze_board_simple()

        # Use complex analysis methods after simple analysis yields no results
        if not self.destinations:
            self.destinations = self.analyze_board_complex()

        print("Destinations:", self.destinations)

        explored_top_row = self.check_explored_top_row()
        if explored_top_row:
            print("Moving to goal")
            self.button_goal.on_click()
            self.destinations = []

        if not self.destinations or self.skull_finder.status != globals.PLAYING or not self.option_auto:
            self.auto_running = False
            self.button_auto.setDisabled(False)
            self.button_auto.setChecked(False)
            self.option_auto = False
            self.auto_timer.stop()
            print("End of auto solve")
            return

        self.destinations = self.sort_destinations()

        # Check if unexplored with each move because cells with 0 will recursively explore adjacent cells with 0
        next_destination = None
        while self.destinations:
            destination_to_check = self.destinations.pop(0)

            # Assume no access to diagonal moves in Skull Finder. Diagonals are technically possible but not intended.
            cardinal_neighbors = self.get_cardinal_neighbors(destination_to_check["row"], destination_to_check["col"])
            unexplored_cardinal_neighbors = [cell for cell in cardinal_neighbors if self.skull_finder.grid_displayed_data[cell["row"]][cell["col"]] != globals.CELL_UNEXPLORED]
            is_bottom_row = destination_to_check["row"] == self.skull_finder.row_size - 1

            if (unexplored_cardinal_neighbors or is_bottom_row) and self.skull_finder.grid_displayed_data[destination_to_check["row"]][destination_to_check["col"]] == globals.CELL_UNEXPLORED:
                next_destination = destination_to_check
                break

        if next_destination:
            print("Moving to:", next_destination["row"], next_destination["col"])
            self.button_grid[next_destination["row"]][next_destination["col"]].on_click()

    def check_explored_top_row(self):
        explored_top_row = []
        for col in range(0, self.skull_finder.col_size):
            if self.skull_finder.grid_displayed_data[globals.TOP_ROW][col] not in [globals.CELL_UNEXPLORED, globals.CELL_EXPLORED_SKULL]:
                explored_top_row.append({"row": globals.TOP_ROW, "col": col})

        return explored_top_row

    def analyze_board_simple(self):
        # Loop 1: The bottom row in Skull Finder is always safe. Mark as safe
        for col in range(0, self.skull_finder.col_size):
            self.auto_grid[self.skull_finder.row_size - 1][col]["safe"] = True

        # Loop 2: Compare cell value with number of unsafe unexplored neighbors
        # If the number of unexplored unsafe neighbors == the cell value, then flag all unexplored unsafe neighbors
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                if self.skull_finder.grid_displayed_data[row][col] not in range(1, 10):
                    continue

                neighbors = self.get_neighbors(row, col)
                neighbors_unexplored = [cell for cell in neighbors if self.skull_finder.grid_displayed_data[cell["row"]][cell["col"]] == globals.CELL_UNEXPLORED]
                neighbors_unexplored_unsafe = [cell for cell in neighbors_unexplored if not self.auto_grid[cell["row"]][cell["col"]]["safe"]]

                if len(neighbors_unexplored_unsafe) == self.skull_finder.grid_displayed_data[row][col]:
                    for neighbor in neighbors_unexplored_unsafe:
                        self.auto_grid[neighbor["row"]][neighbor["col"]]["flag"] = True

        # Loop 3: Compare cell value with number of flagged neighbors
        # If the number of flagged neighbors == the cell value, then mark all non-flagged neighbors as safe.
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                if self.skull_finder.grid_displayed_data[row][col] not in range(1, 10):
                    continue

                neighbors = self.get_neighbors(row, col)
                neighbors_flagged = [cell for cell in neighbors if self.auto_grid[cell["row"]][cell["col"]]["flag"]]
                neighbors_non_flagged = [cell for cell in neighbors if not self.auto_grid[cell["row"]][cell["col"]]["flag"]]

                if len(neighbors_flagged) == self.skull_finder.grid_displayed_data[row][col]:
                    for neighbor in neighbors_non_flagged:
                        self.auto_grid[neighbor["row"]][neighbor["col"]]["safe"] = True

        # Final loop: Add all unexplored safe cells to the destinations list
        destinations = []
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                if self.skull_finder.grid_displayed_data[row][col] == globals.CELL_UNEXPLORED and self.auto_grid[row][col]["safe"]:
                    if self.auto_grid[row][col]["flag"]:
                        raise Exception(f"Cell {row}, {col} is marked as both flagged and safe")

                    destinations.append({"row": row, "col": col})

        return destinations

    def analyze_board_complex(self):
        # Loop 4: Advanced comparison between two cardinal neighbors (no diagonals) with values 1-9.
        for row_1 in range(0, self.skull_finder.row_size):
            for col_1 in range(0, self.skull_finder.col_size):
                if self.skull_finder.grid_displayed_data[row_1][col_1] not in range(1, 10):
                    continue

                cardinal_neighbors = self.get_cardinal_neighbors(row_1, col_1)
                for neighbor in cardinal_neighbors:
                    row_2 = neighbor["row"]
                    col_2 = neighbor["col"]
                    if self.skull_finder.grid_displayed_data[row_2][col_2] not in range(1, 10):
                        continue

                    neighbors_a = self.get_neighbors(row_1, col_1)
                    neighbors_a_flagged = [cell for cell in neighbors_a if self.auto_grid[cell["row"]][cell["col"]]["flag"]]
                    neighbors_a_unexplored = [cell for cell in neighbors_a if self.skull_finder.grid_displayed_data[cell["row"]][cell["col"]] == globals.CELL_UNEXPLORED]
                    neighbors_a_unexplored_non_flagged = [cell for cell in neighbors_a_unexplored if not self.auto_grid[cell["row"]][cell["col"]]["flag"]]

                    neighbors_b = self.get_neighbors(row_2, col_2)
                    neighbors_b_flagged = [cell for cell in neighbors_b if self.auto_grid[cell["row"]][cell["col"]]["flag"]]
                    neighbors_b_unexplored = [cell for cell in neighbors_b if self.skull_finder.grid_displayed_data[cell["row"]][cell["col"]] == globals.CELL_UNEXPLORED]
                    neighbors_b_unexplored_non_flagged = [cell for cell in neighbors_b_unexplored if not self.auto_grid[cell["row"]][cell["col"]]["flag"]]

                    modified_value_a = self.skull_finder.grid_displayed_data[row_1][col_1] - len(neighbors_a_flagged)
                    modified_value_b = self.skull_finder.grid_displayed_data[row_2][col_2] - len(neighbors_b_flagged)

                    neighbors_a_unexplored_non_flagged_exclusive = [cell for cell in neighbors_a_unexplored_non_flagged if cell not in neighbors_b_unexplored_non_flagged]
                    neighbors_b_unexplored_non_flagged_exclusive = [cell for cell in neighbors_b_unexplored_non_flagged if cell not in neighbors_a_unexplored_non_flagged]

                    if modified_value_a - modified_value_b == len(neighbors_a_unexplored_non_flagged_exclusive):
                        for cell in neighbors_a_unexplored_non_flagged_exclusive:
                            self.auto_grid[cell["row"]][cell["col"]]["flag"] = True
                        for cell in neighbors_b_unexplored_non_flagged_exclusive:
                            self.auto_grid[cell["row"]][cell["col"]]["safe"] = True

        # Final loop: Add all unexplored safe cells to the destinations list
        destinations = []
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                if self.skull_finder.grid_displayed_data[row][col] == globals.CELL_UNEXPLORED and self.auto_grid[row][col]["safe"]:
                    if self.auto_grid[row][col]["flag"]:
                        raise Exception(f"Cell {row}, {col} is marked as both flagged and safe")

                    destinations.append({"row": row, "col": col})

        return destinations

    def get_neighbors(self, row: int, col: int):
        neighbors = []
        for x in range(-1, 2):
            if not self.skull_finder.valid_row(row + x):
                continue

            for y in range(-1, 2):
                if not self.skull_finder.valid_col(col + y):
                    continue

                if x == 0 and y == 0:
                    continue

                neighbors.append({"row": row + x, "col": col + y})

        return neighbors

    def get_cardinal_neighbors(self, row: int, col: int):
        neighbors = []
        for x in range(-1, 2):
            if not self.skull_finder.valid_row(row + x):
                continue

            for y in range(-1, 2):
                if not self.skull_finder.valid_col(col + y):
                    continue

                if abs(x) == abs(y):
                    continue

                neighbors.append({"row": row + x, "col": col + y})

        return neighbors

    def sort_destinations(self):
        # Sort destinations by distance from the selected cell + distance from the goal row
        for destination in self.destinations:
            heuristic = destination["row"]
            distance = abs(self.selected_row - destination["row"]) + abs(self.selected_col - destination["col"])
            destination["priority"] = heuristic + distance

        sorted_destinations = sorted(self.destinations, key=lambda x: x["priority"])
        return sorted_destinations

    def pathfind_to_cell(self, target_row: int, target_col: int):
        # Create a graph of currently explored cells and the target cell
        graph = {}
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                if self.skull_finder.grid_displayed_data[row][col] != globals.CELL_UNEXPLORED:
                    graph[(row, col)] = []

        # Connect cardinal neighbors
        for node in graph:
            row = node[0]
            col = node[1]
            neighbors = self.get_cardinal_neighbors(row, col)
            for neighbor in neighbors:
                graph[node].append((neighbor["row"], neighbor["col"]))

        # Pathfind to the target cell using A* algorithm
        start_node = (self.selected_row, self.selected_col)
        end_node = (target_row, target_col)
        path = self.a_star(graph, start_node, end_node)
        return path

    def a_star(self, graph, start, end):
        # TODO
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    app.exec()
