from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLineEdit, QPushButton, QScrollArea, QFrame, QDialogButtonBox
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
        self.tasks_container = QFrame()
        self.tasks_list_layout = QVBoxLayout(self.tasks_container)
        self.tasks_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        tasks_scroll = QScrollArea()
        tasks_scroll.setWidgetResizable(True)
        tasks_scroll.setWidget(self.tasks_container)
        tasks_layout.addWidget(tasks_scroll)

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

    # --- Row UI Component Generators ---

    def create_task_row_ui(self):
        """Generates a layout containing the task widgets."""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 5, 0, 5)

        task_name = QLineEdit()
        task_name.setPlaceholderText("Task Name")
        task_time = QLineEdit()
        task_time.setPlaceholderText("Time (hrs)")
        btn_delete = QPushButton("Delete")

        row_layout.addWidget(task_name)
        row_layout.addWidget(task_time)
        row_layout.addWidget(btn_delete)

        return row_widget

    def create_item_row_ui(self):
        """Generates a layout containing the item widgets."""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 5, 0, 5)

        item_name = QLineEdit()
        item_name.setPlaceholderText("Item Name")
        item_code = QLineEdit()
        item_code.setPlaceholderText("Code")
        item_quantity = QLineEdit()
        item_quantity.setPlaceholderText("Qty")
        btn_delete = QPushButton("Delete")

        row_layout.addWidget(item_name)
        row_layout.addWidget(item_code)
        row_layout.addWidget(item_quantity)
        row_layout.addWidget(btn_delete)

        return row_widget