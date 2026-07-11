from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLineEdit, QPushButton, QScrollArea, QFrame, QDialogButtonBox, QGridLayout, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from database.models import ServiceProjects
from helper_functions import clear_layout, confirmation_dialog
import copy

class ServiceProjectDialog(QDialog):
    refresh_signal = Signal()
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
        self.btn_add_task.clicked.connect(self.add_task)
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
        """self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setText("Save")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Exit")
        main_layout.addWidget(self.button_box)"""
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.exit_button_handler)
        main_layout.addWidget(self.exit_button)

        self.refresh_tasks()
        self.refresh_service_parts()
    def refresh_tasks(self):
        clear_layout(self.tasks_list_layout, grid_layout=True)
        with self.database.session() as session:
            project = session.query(ServiceProjects).get(self.project_id)
            tasks = project.tasks
            counter = 0
            if tasks:
                for index,task in enumerate(tasks):
                    task_name_label = QLabel()
                    task_name_label.setText(task["task_name"])
                    self.tasks_list_layout.addWidget(task_name_label, counter, 0)
                    task_duration_label = QLabel()
                    task_duration_label.setText(f"{task['task_time']} hours" if task['task_time'] else "No duration")
                    self.tasks_list_layout.addWidget(task_duration_label, counter, 1)
                    task_creation_time_label = QLabel()
                    task_creation_time_label.setText(f"{task['task_date']}")
                    self.tasks_list_layout.addWidget(task_creation_time_label, counter, 2)
                    edit_button = QPushButton("Edit")
                    edit_button.clicked.connect(lambda _, task_number=index: self.edit_task(task_number))
                    self.tasks_list_layout.addWidget(edit_button, counter, 3)
                    delete_button = QPushButton("Delete")
                    delete_button.clicked.connect(lambda _, task_number=index: self.delete_task(task_number))
                    self.tasks_list_layout.addWidget(delete_button, counter, 4)
                    counter += 1
            else:
                no_tasks_label = QLabel("No tasks added yet.")
                no_tasks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tasks_list_layout.addWidget(no_tasks_label, 0, 0, 1, 3)
    def refresh_service_parts(self):
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
                    delete_button.clicked.connect(lambda _, part_id=counter: self.delete_service_part(part_id))
                    self.items_list_layout.addWidget(delete_button, counter, 4)
                    counter += 1
            else:
                no_items_label = QLabel("No items added yet.")
                no_items_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.items_list_layout.addWidget(no_items_label, 0, 0, 1, 5)


    def add_task(self):
        dialog = AddTaskDialog(self.database,self.project_id)
        dialog.exec()
        if dialog.result() == QDialog.DialogCode.Accepted:
            self.refresh_tasks()
    def delete_task(self, task_number):
        confirmation = confirmation_dialog(self, "Delete Task", "Are you sure you want to delete this task?")
        if confirmation == QMessageBox.StandardButton.No:
            return
        with self.database.session() as session:
            project = session.query(ServiceProjects).get(self.project_id)
            updated_projects = project.tasks.copy()
            updated_projects.pop(task_number)
            project.tasks = updated_projects
            session.commit()
            self.refresh_tasks()
    def edit_task(self, task_number):
        edit_dialog = EditTaskDialog(self.database,self.project_id,task_number)
        edit_dialog.save_signal.connect(self.refresh_tasks)
        edit_dialog.exec()

    def add_service_part(self):
        pass
    def delete_service_part(self, part_id):
        confirmation = confirmation_dialog(self, "Delete Item", "Are you sure you want to delete this item?")
        if confirmation == QMessageBox.StandardButton.No:
            return
        with self.database.session() as session:
            project = session.query(ServiceProjects).get(self.project_id)
            project.service_parts.pop(part_id)
            session.commit()
            self.refresh_service_parts()

    def exit_button_handler(self):
        self.refresh_signal.emit()
        self.reject()


class AddTaskDialog(QDialog):
    def __init__(self, database, project_id, parent=None, edit=False):
        super().__init__(parent)
        self.database = database
        self.project_id=project_id
        self.parent = parent

        self.setWindowTitle("Add Task")
        self_layout = QGridLayout()
        self.setLayout(self_layout)
        self.task_name_input = QLineEdit()
        self.task_name_input.setPlaceholderText("Task Name")
        self_layout.addWidget(self.task_name_input, 0, 0, 1, 2)
        self.task_time_input = QLineEdit()
        self.task_time_input.setPlaceholderText("Task Time (hours)")
        self_layout.addWidget(self.task_time_input, 1, 0, 1, 2)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_button_handler)
        self_layout.addWidget(self.save_button, 2, 0)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self_layout.addWidget(self.cancel_button, 2, 1)
    def save_button_handler(self):
        task_name = self.task_name_input.text()
        task_time = self.task_time_input.text() or ""
        task_date = datetime.now().strftime("%d-%m-%Y")
        # inputs validation
        if not task_name:
            QMessageBox.warning(self, "Error", "Task name is required.")
            return
        if task_time:
            task_time = task_time.replace(",", ".").strip()
            try:
                task_time = float(task_time)
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid time format. Please use a number.")
                return
        else:
            confirmation = confirmation_dialog(self, "Warning", "No time entered. Are you sure you want to save this task without time?")
            if confirmation == QMessageBox.StandardButton.No:
                return
        try:
            with self.database.session() as session:
                project = session.get(ServiceProjects, self.project_id)
                if not project:
                    QMessageBox.warning(self, "Error", "Project no longer exists.")
                    return
                updated_project_tasks = project.tasks.copy() if project.tasks else []
                new_task = {"task_name": task_name, "task_time": task_time, "task_date": task_date}
                updated_project_tasks.append(new_task)
                project.tasks = updated_project_tasks
                try:
                    session.commit()
                    self.accept()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to save task: {e}")
                    return
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load project: {e}")
            return
class EditTaskDialog(QDialog):
    save_signal = Signal()
    def __init__(self, database, project_id,task_number ,parent=None):
        super().__init__(parent)
        self.database = database
        self.project_id=project_id
        self.task_number = task_number
        self.parent = parent

        with self.database.session() as session:
            task = session.query(ServiceProjects).get(self.project_id).tasks[self.task_number]

        self.setWindowTitle("Edit Task")
        self_layout = QGridLayout()
        self.setLayout(self_layout)
        self.task_name_input = QLineEdit()
        self.task_name_input.setText(task["task_name"])
        self_layout.addWidget(self.task_name_input, 0, 0, 1, 2)
        self.task_time_input = QLineEdit()
        self.task_time_input.setText(str(task["task_time"]) if task["task_time"] else "")
        self_layout.addWidget(self.task_time_input, 1, 0, 1, 2)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(lambda: self.save_button_handler(self.task_number))
        self_layout.addWidget(self.save_button, 2, 0)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self_layout.addWidget(self.cancel_button, 2, 1)
    def save_button_handler(self, task_number):
        task_name = self.task_name_input.text()
        task_time = self.task_time_input.text() or ""
        with self.database.session() as session:
            # update entire list of tasks
            project = session.get(ServiceProjects, self.project_id)
            tasks = project.tasks
            updated_task = copy.deepcopy(tasks)
            updated_task[task_number]["task_name"] = task_name
            updated_task[task_number]["task_time"] = task_time.replace(",", ".").strip() if task_time else None
            project.tasks = updated_task
            session.commit()
        self.save_signal.emit()
        self.accept()







