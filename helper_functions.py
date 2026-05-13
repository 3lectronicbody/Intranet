from PySide6.QtWidgets import QMessageBox
from pathlib import Path



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

def load_css(file_path):
    absolute_path = Path(file_path)
    try:
        with open(absolute_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {absolute_path}")










