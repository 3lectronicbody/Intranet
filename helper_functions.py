from PySide6.QtWidgets import QMessageBox, QDialog, QGridLayout, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, \
    QPushButton
from PySide6.QtCore import Signal
from database.models import ProjectDetails


def clear_layout(layout, grid_layout=False):
    # grid_layout=False will delete all widgets in the layout
    # grid_layout=True will delete all widgets and clear stretch factors if layout is QGridLayout
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
        elif child.layout():
            clear_layout(child.layout())
    if grid_layout:
        # clear stretch factors for rows
        for i in range(layout.rowCount()):
            layout.setRowStretch(i, 0)
            layout.setRowMinimumHeight(i, 0)
        # clear stretch factors for columns
        for j in range(layout.columnCount()):
            layout.setColumnStretch(j, 0)
            layout.setColumnMinimumWidth(j, 0)

def confirmation_dialog(parent, title, message,):
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    return dialog.exec()











