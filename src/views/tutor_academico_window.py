from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow


class MainWindow_TutorAcademico(QMainWindow):  # noqa: N801
    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
