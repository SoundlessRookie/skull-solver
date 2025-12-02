import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QToolButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Skull Solver")
        self.setFixedSize(QSize(500, 500))

        # TODO: Create grid
        button = QToolButton()
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        button.setIcon(QPixmap("assets/cell-64x64-0.png"))
        button.setIconSize(QSize(64, 64))
        button.setFixedSize(QSize(64, 64))
        button.setCheckable(True)
        button.setDisabled(True)
        button.clicked.connect(self.button_click)
        button.toggled.connect(self.button_toggle)

        self.is_button_checked = False

        self.setCentralWidget(button)

    @staticmethod
    def button_click():
        print("Button Clicked")

    def button_toggle(self, checked):
        self.is_button_checked = checked
        print("Checked?", self.is_button_checked)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
