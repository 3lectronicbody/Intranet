from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLineEdit, QPushButton, QScrollArea, QFrame, QDialogButtonBox, QGridLayout, QLabel
)
from PySide6.QtCore import Qt

from database.models import ServiceProjects
from helper_functions import clear_layout


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
        self.items_list_layout = QGridLayout(self.items_container)
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

        self.refresh_tasks()
        self.refresh_items()
    def refresh_tasks(self):
        clear_layout(self.tasks_list_layout, grid_layout=True)
        with self.database.session() as session:
            project = session.query(ServiceProjects).get(self.project_id)
            tasks = project.tasks
            counter = 0
            if tasks:
                for name, time in tasks.items():
                    task_label = QLabel(f"{name}: {time} hr")
                    self.tasks_list_layout.addWidget(task_label, counter, 0)
                    edit_button = QPushButton("Edit")
                    self.tasks_list_layout.addWidget(edit_button, counter, 1)
                    delete_button = QPushButton("Delete")
                    self.tasks_list_layout.addWidget(delete_button, counter, 2)
                    counter += 1
            else:
                no_tasks_label = QLabel("No tasks added yet.")
                no_tasks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tasks_list_layout.addWidget(no_tasks_label, 0, 0, 1, 3)
    def refresh_items(self):
        clear_layout(self.items_list_layout, grid_layout=True)
        with self.database.session() as session:
            project = session.query(ServiceProjects).get(self.project_id)
            service_parts_list = project.service_parts
            counter = 0
            if service_parts_list:
                for part in service_parts_list:
                    part_name_label = QLabel(part[0] or "")
                    part_code_label = QLabel(part[1] or "")
                    part_quantity_label = QLabel(part[2] or "")
                    self.items_list_layout.addWidget(part_name_label, counter, 0)
                    self.items_list_layout.addWidget(part_code_label, counter, 1)
                    self.items_list_layout.addWidget(part_quantity_label, counter, 2)
                    edit_button = QPushButton("Edit")
                    self.items_list_layout.addWidget(edit_button, counter, 3)
                    delete_button = QPushButton("Delete")
                    self.items_list_layout.addWidget(delete_button, counter, 4)
                    counter += 1
            else:
                no_items_label = QLabel("No items added yet.")
                no_items_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.items_list_layout.addWidget(no_items_label, 0, 0, 1, 5)



