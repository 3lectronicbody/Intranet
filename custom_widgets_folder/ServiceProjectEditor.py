from PySide6 import QtGui, QtCore
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLineEdit, QPushButton, QScrollArea, QFrame,QTextEdit, QGridLayout, QLabel, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal
from helper_functions import clear_layout, confirmation_dialog
import copy
from pathlib import Path
import pypdf
import io
from datetime import datetime
import tempfile
from config import API_PATH
import requests



class ServiceProjectDialog(QDialog):
    # Main Window
    refresh_signal = Signal()
    def __init__(self, user_id, project_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Service Project Editor")
        self.resize(1000, 700)

        self.user_id = user_id
        self.project_id = project_id
        self.parent = parent
        self.create_pdf_slot = None
        self.open_pdf_slot = None


        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)

        self.left_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout,1)
        self.edit_project = EditServiceProject(self.user_id, self.project_id)
        self.edit_project.save_signal.connect(self.edit_project.refresh)
        self.left_layout.addWidget(self.edit_project)
        # Right Layout
        self.right_layout = QVBoxLayout()
        self.main_layout.addLayout(self.right_layout,2)

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
        self.right_layout.addWidget(tasks_group)

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

        self.add_service_part = QPushButton("Add Service Part")
        self.add_service_part.clicked.connect(self.add_service_part_handler)
        items_layout.addWidget(self.add_service_part)
        self.right_layout.addWidget(items_group)

        # ==========================================
        # 3. BOTTOM BUTTON LAYOUT
        # ==========================================

        self.button_layout = QHBoxLayout()
        self.right_layout.addLayout(self.button_layout)
        self.complete_activate_button = QPushButton("")
        self.button_layout.addWidget(self.complete_activate_button)

        self.open_pdf_form_button = QPushButton("Open PDF Form")
        self.button_layout.addWidget(self.open_pdf_form_button)

        self.erase_project_button = QPushButton("Erase Project...")
        self.button_layout.addWidget(self.erase_project_button)
        self.erase_project_button.clicked.connect(self.erase_button_handler)



        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.exit_button_handler)
        self.right_layout.addWidget(self.back_button)

        self.refresh_tasks()
        self.refresh_service_parts()
        self.refresh()
    def refresh_tasks(self):
        clear_layout(self.tasks_list_layout, grid_layout=True)
        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        project_data = response.json()
        tasks = project_data.get('tasks')
        counter = 0
        if tasks:
            for index,task in enumerate(tasks):
                    task_name_label = QLabel()
                    task_name_label.setText(task["task_name"])
                    task_name_label.setStyleSheet("font-weight: bold;")
                    task_name_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                    # create dyn property .menu of task_name_label
                    task_name_label.menu = TaskContextMenu(index, self)
                    task_name_label.customContextMenuRequested.connect(
                    lambda qpoint, label = task_name_label: task_name_label.menu.exec(label.mapToGlobal(qpoint))
                    )
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
        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        project_data = response.json()
        service_parts_list = project_data.get('service_parts')
        counter = 0
        if service_parts_list:
            for part in service_parts_list:
                    part_name_label = QLabel(part['name'] or "")
                    part_name_label.setStyleSheet("font-weight: bold;")
                    part_name_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                    # crete dyn property .menu of task_name_label
                    part_name_label.menu = ServicePartContextMenu(counter, self)
                    part_name_label.customContextMenuRequested.connect(
                        lambda qpoint, label=part_name_label: part_name_label.menu.exec(label.mapToGlobal(qpoint))
                    )
                    part_code_label = QLabel(part['code'] or "")
                    part_quantity_label = QLabel(str(part['quantity']) or "")
                    self.items_list_layout.addWidget(part_name_label, counter, 0)
                    self.items_list_layout.addWidget(part_code_label, counter, 1)
                    self.items_list_layout.addWidget(part_quantity_label, counter, 2)
                    edit_button = QPushButton("Edit")
                    edit_button.clicked.connect(lambda _, part_id=counter: self.edit_service_part(part_id))
                    self.items_list_layout.addWidget(edit_button, counter, 3)
                    delete_button = QPushButton("Delete")
                    delete_button.clicked.connect(lambda _, part_id=counter: self.delete_service_part(part_id))
                    self.items_list_layout.addWidget(delete_button, counter, 4)
                    counter += 1
        else:
            no_items_label = QLabel("No items added yet.")
            no_items_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.items_list_layout.addWidget(no_items_label, 0, 0, 1, 5)
    def refresh(self):
        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        project = response.json()
        if project['active']:
            self.complete_activate_button.setText("Complete")
            self.complete_activate_button.clicked.connect(self.deactivate_service_project)

        else:
            self.complete_activate_button.setText("Activate")
            self.complete_activate_button.clicked.connect(self.activate_service_project)

        if not project.get('pdf_form'):
            self.open_pdf_form_button.setText("Create PDF Form")
            self.open_pdf_form_button.clicked.connect(self.create_pdf_form)
        else:
            self.open_pdf_form_button.setText("Open PDF Form")
            self.open_pdf_form_button.clicked.connect(self.open_pdf_form)

    def add_task(self):
        dialog = AddTaskDialog(self.project_id)
        dialog.exec()
        if dialog.result() == QDialog.DialogCode.Accepted:
            self.refresh_tasks()
    def delete_task(self, task_number):
        confirmation = confirmation_dialog(self, "Delete Task", "Are you sure you want to delete this task?")
        if confirmation == QMessageBox.StandardButton.No:
            return
        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        project = response.json()
        updated_tasks = project.get('tasks', []).copy()
        updated_tasks.pop(task_number)
        requests.patch(f"{API_PATH}/service_project/{self.project_id}", json={'tasks': updated_tasks})
        self.refresh_tasks()
    def edit_task(self, task_number):
        edit_dialog = EditTaskDialog(self.project_id,task_number)
        edit_dialog.save_signal.connect(self.refresh_tasks)
        edit_dialog.exec()
    def edit_service_part(self, part_id):
        edit_dialog = EditServicePartDialog(self.project_id,part_id)
        edit_dialog.save_signal.connect(self.refresh_service_parts)
        edit_dialog.exec()
    def add_service_part_handler(self):
        add_service_part_dialog = AddServicePartDialog(self.project_id)
        add_service_part_dialog.refresh_signal.connect(self.refresh_service_parts)
        add_service_part_dialog.exec()
    def delete_service_part(self, part_id):
        confirmation = confirmation_dialog(self, "Delete Item", "Are you sure you want to delete this item?")
        if confirmation == QMessageBox.StandardButton.No:
            return
        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        project = response.json()
        service_parts = copy.deepcopy(project.get('service_parts', []))
        service_parts.pop(part_id)
        requests.patch(f"{API_PATH}/service_project/{self.project_id}", json={'service_parts': service_parts})
        self.refresh_service_parts()
    def exit_button_handler(self):
        self.refresh_signal.emit()
        self.reject()
    def activate_service_project(self):
        confirmation = confirmation_dialog(self, "Activate Service Project",
                                           f"Are you sure you want to activate Service Project ")

        if confirmation == QMessageBox.StandardButton.Yes:
            requests.patch(f"{API_PATH}/service_project/{self.project_id}", json={'active': True, 'end_date': None})
            self.refresh_signal.emit()
            self.complete_activate_button.clicked.disconnect(self.activate_service_project)
            self.refresh()
        else:
            self.refresh()
    def deactivate_service_project(self):
        confirmation = confirmation_dialog(self, "Complete Service Project",
                                           f"Are you sure you want to deactivate Service Project")

        if confirmation == QMessageBox.StandardButton.Yes:
            requests.patch(f"{API_PATH}/service_project/{self.project_id}", json={'active': False, 'end_date': datetime.now().isoformat()})
            self.refresh_signal.emit()
            self.complete_activate_button.clicked.disconnect(self.deactivate_service_project)
            self.refresh()

        else:
            self.refresh()
    def erase_button_handler(self):
        warning = confirmation_dialog(self, "Erase Service Project",
                                           f"Are you sure you want to erase Service Project?\n"
                                           f"This action cannot be undone !!!")

        if warning == QMessageBox.StandardButton.Yes:
            requests.delete(f"{API_PATH}/service_project/{self.project_id}")
            self.refresh_signal.emit()
            self.accept()

    def open_pdf_form(self):
        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        project = response.json()
        if project and project.get('pdf_form'):
            import base64
            pdf_data = base64.b64decode(project['pdf_form'])
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(pdf_data)
                temp_path = temp_file.name
                QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(temp_path))
            self.open_pdf_form_button.clicked.disconnect(self.open_pdf_form)
        else:
            print("PDF form not found.")

    def create_pdf_form(self):
        confirmation = confirmation_dialog(self, "Confirmation", "Are you sure you want to generate the PDF form?")
        if confirmation == QMessageBox.StandardButton.Yes:
            response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
            project = response.json()
            current_dir = Path(__file__).parent
            empty_pdf_form_path = current_dir.parent / "files" / "service_form.pdf"
            pdf_reader = pypdf.PdfReader(empty_pdf_form_path)
            writer = pypdf.PdfWriter()
            writer.append(pdf_reader)

            start_date_dt = datetime.fromisoformat(project['start_date'])

            data = {"number": (project['number'][-3:]),
                    "year": project['number'][2:4],
                    "start_date": start_date_dt.strftime("%d-%m-%Y"),
                    "owner": project['owner'],
                    "phone_number": project['phone_number'],
                    "email": project['email'],
                    "manufacturer": project['manufacturer'],
                    "model": project['model'],
                    "code": project['code'],
                    "serial_number": project['serial_number'],
                    "description": project['description']
                    }
            # Fulfill form values with data
            writer.update_page_form_field_values(writer.pages[0], data)

            # Saving the Pdf to a BytesIO object and then to a database field
            bytes_stream = io.BytesIO()  # create a BytesIO object
            writer.write(bytes_stream)  # write pdf content to the BytesIO object

            import base64
            requests.patch(f"{API_PATH}/service_project/{self.project_id}", json={'pdf_form': base64.b64encode(bytes_stream.getvalue()).decode('utf-8')})
            self.open_pdf_form_button.clicked.disconnect(self.create_pdf_form)
            self.refresh()
        else:
            self.open_pdf_form_button.clicked.disconnect(self.create_pdf_form)
            self.refresh()

class EditServiceProject(QWidget):
    # left side of ServiceProjectDialog, where user can edit the project details
    save_signal = Signal()

    def __init__(self, user_id, project_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.project_id = project_id
        self.parent = parent

        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        self.project = response.json()

        self.current_values = {'owner': self.project['owner'].strip(),
                               'phone_number': self.project['phone_number'].strip(),
                               'email': self.project['email'].strip(),
                               'manufacturer': self.project['manufacturer'].strip(),
                               'model': self.project['model'].strip(),
                               'code': self.project['code'].strip(),
                               'serial_number': self.project['serial_number'].strip(),
                               'description': self.project['description'].strip()}

        self.setWindowTitle("Edit Service Project")

        self.main_layout_vertical = QVBoxLayout()
        self.setLayout(self.main_layout_vertical)

        self.layout = QGridLayout()
        self.main_layout_vertical.addLayout(self.layout)
        self.number_title_label = QLabel("Number: ")
        self.layout.addWidget(self.number_title_label, 0, 0)

        self.number_input = QLineEdit()
        self.number_input.setText(self.project['number'])
        self.number_input.setStyleSheet("color: #3498db; font-weight: bold;")
        self.number_input.setReadOnly(True)
        self.layout.addWidget(self.number_input, 0, 1)

        self.receive_date_label = QLabel("Date:")
        self.layout.addWidget(self.receive_date_label, 1, 0)
        self.receive_date_input = QLineEdit()
        import datetime
        start_date = datetime.datetime.fromisoformat(self.project['start_date'])
        self.receive_date_input.setText(start_date.strftime("%d-%m-%Y"))
        self.receive_date_input.setStyleSheet("color: #3498db;")
        self.receive_date_input.setReadOnly(True)
        self.layout.addWidget(self.receive_date_input, 1, 1)

        self.inputs = []

        self.owner_label = QLabel("Owner: ")
        self.layout.addWidget(self.owner_label, 2, 0)
        self.owner_input = QLineEdit()
        self.layout.addWidget(self.owner_input, 2, 1)
        self.inputs.append(self.owner_input)

        self.phone_number_label = QLabel("Phone Number: ")
        self.layout.addWidget(self.phone_number_label, 3, 0)
        self.phone_number_input = QLineEdit()
        self.layout.addWidget(self.phone_number_input, 3, 1)
        self.inputs.append(self.phone_number_input)

        self.email_label = QLabel("Email: ")
        self.layout.addWidget(self.email_label, 4, 0)
        self.email_input = QLineEdit()
        self.layout.addWidget(self.email_input, 4, 1)
        self.inputs.append(self.email_input)

        self.manufacturer_label = QLabel("Manufacturer: ")
        self.layout.addWidget(self.manufacturer_label, 5, 0)
        self.manufacturer_input = QLineEdit()
        self.layout.addWidget(self.manufacturer_input, 5, 1)
        self.inputs.append(self.manufacturer_input)

        self.model_label = QLabel("Model: ")
        self.layout.addWidget(self.model_label, 6, 0)
        self.model_input = QLineEdit()
        self.layout.addWidget(self.model_input, 6, 1)
        self.inputs.append(self.model_input)

        self.code_label = QLabel("Code: ")
        self.layout.addWidget(self.code_label, 7, 0)
        self.code_input = QLineEdit()
        self.layout.addWidget(self.code_input, 7, 1)
        self.inputs.append(self.code_input)

        self.serial_number_label = QLabel("Serial Number: ")
        self.layout.addWidget(self.serial_number_label, 8, 0)
        self.serial_number_input = QLineEdit()
        self.layout.addWidget(self.serial_number_input, 8, 1)
        self.inputs.append(self.serial_number_input)

        self.description_label = QLabel("Description: ")
        self.layout.addWidget(self.description_label, 9, 0)
        self.description_input = QTextEdit()
        self.layout.addWidget(self.description_input, 9, 1)
        self.inputs.append(self.description_input)

        self.main_layout_vertical.addStretch(1)

        self.refresh()

        # self.inputs.append(self.description_input)
        for i in self.inputs:
            i.textChanged.connect(self.text_changed)

    def refresh(self):
        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        self.project = response.json()
        self.owner_input.setText(self.project['owner'])
        self.phone_number_input.setText(self.project['phone_number'])
        self.email_input.setText(self.project['email'])
        self.manufacturer_input.setText(self.project['manufacturer'])
        self.model_input.setText(self.project['model'])
        self.code_input.setText(self.project['code'])
        self.serial_number_input.setText(self.project['serial_number'])
        self.description_input.setText(self.project['description'])

    def text_changed(self):
        if self.current_values['owner'] != self.owner_input.text().strip() or \
                self.current_values['phone_number'] != self.phone_number_input.text().strip() or \
                self.current_values['email'] != self.email_input.text().strip() or \
                self.current_values['manufacturer'] != self.manufacturer_input.text().strip() or \
                self.current_values['model'] != self.model_input.text().strip() or \
                self.current_values['code'] != self.code_input.text().strip() or \
                self.current_values['serial_number'] != self.serial_number_input.text().strip() or \
                self.current_values['description'] != self.description_input.toPlainText().strip():
            data = {
                'owner': self.owner_input.text(),
                'phone_number': self.phone_number_input.text(),
                'email': self.email_input.text(),
                'manufacturer': self.manufacturer_input.text(),
                'model': self.model_input.text(),
                'code': self.code_input.text(),
                'serial_number': self.serial_number_input.text(),
                'description': self.description_input.toPlainText()
            }
            requests.patch(f"{API_PATH}/service_projects/{self.project_id}", json=data)

            # Update current state dictionary:
            self.current_values = {'owner': self.owner_input.text().strip(),
                                   'phone_number': self.phone_number_input.text().strip(),
                                   'email': self.email_input.text().strip(),
                                   'manufacturer': self.manufacturer_input.text().strip(),
                                   'model': self.model_input.text().strip(),
                                   'code': self.code_input.text().strip(),
                                   'serial_number': self.serial_number_input.text().strip(),
                                   'description': self.description_input.toPlainText().strip()}

class AddTaskDialog(QDialog):
    def __init__(self, project_id, parent=None):
        super().__init__(parent)
        self.project_id=project_id
        self.parent = parent

        self.setWindowTitle("Add Task")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.task_name_input = QLineEdit()
        self.task_name_input.setPlaceholderText("Name...")
        self.layout.addWidget(self.task_name_input, 0, 0, 1, 2)
        self.task_time_input = QLineEdit()
        self.task_time_input.setPlaceholderText("Time(h)...")
        self.layout.addWidget(self.task_time_input, 1, 0, 1, 2)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_button_handler)
        self.layout.addWidget(self.save_button, 2, 0)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel_button, 2, 1)
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

        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        project = response.json()
        if not project:
            QMessageBox.warning(self, "Error", "Project no longer exists.")
            return
        updated_project_tasks = project.get('tasks', []) or []
        new_task = {"task_name": task_name, "task_time": task_time, "task_date": task_date}
        updated_project_tasks.append(new_task)
        requests.patch(f"{API_PATH}/service_projects/{self.project_id}", json={'tasks': updated_project_tasks})
        self.accept()
class EditTaskDialog(QDialog):
    save_signal = Signal()
    def __init__(self, project_id,task_number ,parent=None):
        super().__init__(parent)
        self.project_id=project_id
        self.task_number = task_number
        self.parent = parent

        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        task = response.json()['tasks'][self.task_number]

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

        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        project = response.json()
        tasks = project.get('tasks', [])
        updated_tasks = copy.deepcopy(tasks)
        updated_tasks[task_number]["task_name"] = task_name
        updated_tasks[task_number]["task_time"] = task_time.replace(",", ".").strip() if task_time else None

        requests.patch(f"{API_PATH}/service_projects/{self.project_id}", json={'tasks': updated_tasks})
        self.accept()
        self.save_signal.emit()
class AddServicePartDialog(QDialog):
    refresh_signal = Signal()
    def __init__(self, project_id, parent=None):
        super().__init__(parent)
        self.project_id=project_id
        self.parent = parent
        self.setWindowTitle("Add Service Part")

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.part_name_input = QLineEdit()
        self.part_name_input.setPlaceholderText("Name...")
        self.layout.addWidget(self.part_name_input, 0, 0, 1, 2)
        self.part_code_input = QLineEdit()
        self.part_code_input.setPlaceholderText("Code...")
        self.layout.addWidget(self.part_code_input, 1, 0, 1, 2)
        self.service_part_quantity_input = QLineEdit()
        self.service_part_quantity_input.setPlaceholderText("Quantity...")
        self.layout.addWidget(self.service_part_quantity_input, 2, 0, 1, 2)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_button_handler)
        self.layout.addWidget(self.save_button, 3, 0)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel_button, 3, 1)
    def save_button_handler(self):
        part_name = self.part_name_input.text()
        part_code = self.part_code_input.text()
        part_quantity = self.service_part_quantity_input.text().replace(",", ".").strip()
        if not part_name:
            QMessageBox.warning(self, "Error", "Service Part name is required.")
            return
        if not part_quantity:
            QMessageBox.warning(self, "Error", "Service Part quantity is required.")
            return

        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        project = response.json()
        if not project:
            QMessageBox.warning(self, "Error", "Project no longer exists.")
            return

        try:
            part_quantity = float(part_quantity)
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid quantity format. Please use a number.")
            return

        updated_service_parts = copy.deepcopy(project.get('service_parts', [])) if project.get('service_parts') else []
        updated_service_parts.append({"name": part_name, "code": part_code, "quantity": part_quantity})

        requests.patch(f"{API_PATH}/service_projects/{self.project_id}", json={'service_parts': updated_service_parts})
        self.accept()
        self.refresh_signal.emit()
class EditServicePartDialog(QDialog):
    save_signal = Signal()
    def __init__(self, project_id, part_number, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.part_number = part_number
        self.parent = parent

        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        part = response.json()['service_parts'][self.part_number]

        self.setWindowTitle("Edit Task")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.part_name_input = QLineEdit()
        self.part_name_input.setText(part["name"])
        self.layout.addWidget(self.part_name_input, 0, 0, 1, 2)

        self.part_code_input = QLineEdit()
        self.part_code_input.setText(part["code"])
        self.layout.addWidget(self.part_code_input, 1, 0, 1, 2)

        self.part_quantity_input = QLineEdit()
        self.part_quantity_input.setText(str(part["quantity"]) if part["quantity"] else "")
        self.layout.addWidget(self.part_quantity_input, 2, 0, 1, 2)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(lambda: self.save_button_handler(self.part_number))
        self.layout.addWidget(self.save_button, 3, 0)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel_button, 3, 1)

    def save_button_handler(self, part_number):
        part_name = self.part_name_input.text()
        part_code = self.part_code_input.text()
        part_quantity = self.part_quantity_input.text() or ""

        response = requests.get(f"{API_PATH}/service_projects/{self.project_id}")
        project = response.json()
        parts = project.get('service_parts', [])
        updated_parts = copy.deepcopy(parts)
        updated_parts[part_number]["name"] = part_name
        updated_parts[part_number]["code"] = part_code
        updated_parts[part_number]["quantity"] = part_quantity.replace(",", ".").strip() if part_quantity else None

        requests.patch(f"{API_PATH}/service_projects/{self.project_id}", json={'service_parts': updated_parts})
        self.save_signal.emit()
        self.accept()

class TaskContextMenu(QMenu):
    def __init__(self, task_number, parent=None):
        super().__init__(parent)

        self.task_number = task_number
        self.parent = parent
        self.edit_action = QAction("Edit", self)
        self.edit_action.triggered.connect(lambda: self.parent.edit_task(self.task_number))
        self.delete_action = QAction("Delete", self)
        self.delete_action.triggered.connect(lambda: self.parent.delete_task(self.task_number))
        self.addAction(self.edit_action)
        self.addSeparator()
        self.addAction(self.delete_action)
        self.addSeparator()

class ServicePartContextMenu(QMenu):
    def __init__(self, part_number, parent=None):
        super().__init__(parent)

        self.part_number = part_number
        self.parent = parent
        self.edit_action = QAction("Edit", self)
        self.edit_action.triggered.connect(lambda: self.parent.edit_service_part(self.part_number))

        self.delete_action = QAction("Delete", self)
        self.delete_action.triggered.connect(lambda: self.parent.delete_service_part(self.part_number))
        self.addAction(self.edit_action)
        self.addSeparator()
        self.addAction(self.delete_action)
        self.addSeparator()










