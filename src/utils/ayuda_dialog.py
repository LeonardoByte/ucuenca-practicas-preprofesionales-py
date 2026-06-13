from PyQt6 import uic
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog


def mostrar_ayuda_dialog(view, index: int) -> None:
    dialog = QDialog(view)
    uic.loadUi("src/views/ui/wgt_ayuda_acerca.ui", dialog)
    dialog.stackedWidgetAyuda.setCurrentIndex(index)
    dialog.pushButton.clicked.connect(dialog.accept)

    if index == 2:
        QDesktopServices.openUrl(QUrl("https://github.com/LeonardoByte"))

    if index == 3:
        QDesktopServices.openUrl(QUrl("https://github.com/LeonardoByte/ucuenca-practicas-preprofesionales-py"))

    dialog.exec()
