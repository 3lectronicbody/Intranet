from PySide6.QtWidgets import QMessageBox, QDialog, QGridLayout, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, \
    QPushButton
from PySide6.QtCore import Signal

from database.models import ProjectDetails


def clear_layout(layout, grid_layout=False):
    # grid_layout=False will delete all widgets in the layout
    # grid_layout=True will delete all widgets and clear stretch factors in QGridLayout
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

class AddItemActivity(QDialog):
    save_signal = Signal()
    def __init__(self, database, project_id, user_id, flag=None):
        super().__init__()
        self.database = database
        self.project_id = project_id
        self.user_id = user_id

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.data_layout = QGridLayout()
        self.layout.addLayout(self.data_layout)

        self.name_label = QLabel("Name: ")
        self.data_layout.addWidget(self.name_label, 0, 0)
        self.name_input = QLineEdit()
        self.data_layout.addWidget(self.name_input, 0, 1)
        if flag == "item":
            self.code_label = QLabel("Code: ")
            self.data_layout.addWidget(self.code_label, 1, 0)
            self.code_input = QLineEdit()
            self.data_layout.addWidget(self.code_input, 1, 1)
            self.quantity_label = QLabel("Quantity: ")
            self.data_layout.addWidget(self.quantity_label, 2, 0)
            self.setWindowTitle("Add Item")
        elif flag == "activity":
            self.setWindowTitle("Add Activity")
            self.quantity_label = QLabel("Time: ")
            self.data_layout.addWidget(self.quantity_label, 2, 0)

        self.quantity_input = QLineEdit()
        self.data_layout.addWidget(self.quantity_input, 2, 1)

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)

        self.save_button = QPushButton("Save")
        self.buttons_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)
        self.cancel_button = QPushButton("Cancel")
        self.buttons_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self, flag=None):
        if flag == "item":
            name = self.name_input.text() or None
            code = self.code_input.text() or None
            quantity = self.quantity_input.text() or None
        elif flag == "activity":
            name = self.name_input.text() or None
            code = None
            quantity = self.quantity_input.text() or None

        with self.database.session() as session:
            new = ProjectDetails(project_id=self.project_id,
                                name=name,
                                code=code,
                                quantity=quantity)
            session.add(new)
            session.commit()








