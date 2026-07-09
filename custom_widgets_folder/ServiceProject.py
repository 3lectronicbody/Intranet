from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLineEdit, QPushButton, QScrollArea, QFrame, QDialogButtonBox, QGridLayout
)
from PySide6.QtCore import Qt


class ServiceProjectDialog(QDialog):
    def __init__(self,database, user_id, project_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Service Project Editor")
        self.resize(600, 700)

        self.database = database
        self.user_id = user_id
        self.project_id= project_id
        self.parent = parent

        # Main Layout
        main_layout = QVBoxLayout(self)

        # ==========================================
        # 1. TASKS SECTION
        # ==========================================
        tasks_group = QGroupBox("TASKS")
        tasks_group.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centers the "TASKS" title
        tasks_layout = QVBoxLayout()
        tasks_group.setLayout(tasks_layout)

        # Square container frame for task rows
        tasks_scroll = QScrollArea()
        tasks_scroll.setWidgetResizable(True)
        tasks_layout.addWidget(tasks_scroll)

        self.tasks_container = QFrame()
        self.tasks_list_layout = QGridLayout()
        self.tasks_container.setLayout(self.tasks_list_layout)
        self.tasks_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        tasks_scroll.setWidget(self.tasks_container)



        # Bottom of task frame button
        self.btn_add_task = QPushButton("Add Task")
        tasks_layout.addWidget(self.btn_add_task)
        main_layout.addWidget(tasks_group)

        # ==========================================
        # 2. ITEMS SECTION
        # ==========================================
        items_group = QGroupBox("ITEMS")
        items_group.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centers the "ITEMS" title
        items_layout = QVBoxLayout(items_group)

        # Square container frame for item rows
        self.items_container = QFrame()
        self.items_list_layout = QVBoxLayout(self.items_container)
        self.items_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        items_scroll = QScrollArea()
        items_scroll.setWidgetResizable(True)
        items_scroll.setWidget(self.items_container)
        items_layout.addWidget(items_scroll)

        # Bottom of item frame button
        self.btn_add_item = QPushButton("Add Item")
        items_layout.addWidget(self.btn_add_item)
        main_layout.addWidget(items_group)

        # ==========================================
        # 3. BOTTOM BUTTON LAYOUT
        # ==========================================
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setText("Save")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Exit")
        main_layout.addWidget(self.button_box)

