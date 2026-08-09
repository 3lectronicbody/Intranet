import os, sys
from types import SimpleNamespace

from PySide6.QtWidgets import QVBoxLayout, QDialog, QGridLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QComboBox, \
    QMenuBar, QFileDialog, QMessageBox, QApplication, QTextEdit
from PySide6.QtCore import Signal, Qt
from fpdf import FPDF
from API.api import API_CLIENT
from API.pydantic_models import ProjectItemSchema, ProjectActivitySchema
import metadata
from helper_functions import confirmation_dialog, check_for_updates
import requests


class MenuBar(QMenuBar):
    def __init__(self,parent, user_id, project_id=None, flag=None):
        # flag=project: Menu bar for project window
        # flag=main: Menu bar for main menu
        super().__init__()

        self.parent = parent
        self.project_id = project_id
        self.user_id = user_id
        self.flag = flag
        self.app_version = metadata.VERSION

        self.setStyleSheet("background-color: #2c3e50; border-radius: 2px;")
        # ADD FILE MENU TO MENU BAR
        self.file_menu = self.addMenu("File")

        if self.flag == "project":
            self.export_project = self.file_menu.addAction("Export Project...")
            self.export_project.triggered.connect(self.export_project_handler)

        # File Menu -> About Action
        self.about = self.file_menu.addAction("About...")
        self.about.triggered.connect(self.open_about_menu_handler)

        # File Menu -> Exit Action
        self.exit = self.file_menu.addAction("Exit")
        self.exit.triggered.connect(lambda _: self.exit_button_handler())

        self.check_for_updates = self.file_menu.addAction("Check for Updates...")
        self.check_for_updates.triggered.connect(self.update_handler)


    def export_project_handler(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(self)
        if file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)


            items = API_CLIENT.get(f"/projects/{self.project_id}/items/").json()
            items = [SimpleNamespace(**item) for item in items]
            activities = API_CLIENT.get(f"/projects/{self.project_id}/activities/").json()
            activities = [SimpleNamespace(**activity) for activity in activities]
            project_name = API_CLIENT.get(f"/projects/{self.project_id}").json()["name"]

            item_column_width = {"name": 60, "quantity": 20, "code": 40, "unit": 20}

            pdf.cell(100,10,text="PROJECT REPORT",ln=1,align="C")

            pdf.cell(100, 10, txt=f"Project Name: {project_name}", ln=1)
            pdf.cell(100, 10, txt="ITEMS", ln=1)

            for i in items:
                pdf.cell(item_column_width["name"], 10, txt=i.name or "", ln=0)
                pdf.cell(item_column_width["quantity"], 10, txt=str(i.quantity), ln=0)
                pdf.cell(item_column_width["code"], 10, txt=i.code or "", ln=0)
                pdf.cell(item_column_width["unit"], 10, txt=i.unit or "", ln=1)


            activity_column_width = {"name": 60, "quantity": 20}
            pdf.cell(100, 10, txt="ACTIVITIES", ln=1)

            for i in activities:
                pdf.cell(activity_column_width["name"], 10, txt=i.name or "", ln=0)
                pdf.cell(activity_column_width["quantity"], 10, txt=str(i.time), ln=1)

            if file_path[-4:] != ".pdf":
                file_path += ".pdf"

            pdf.output(file_path)
    def open_about_menu_handler(self):
        about_dialog = self.AboutDialog()
        about_dialog.exec()

    @staticmethod
    def exit_button_handler():
        app_instance = QApplication.instance()
        if app_instance:
            app_instance.quit()
    def update_handler(self):
        check = check_for_updates()
        if check:
            confirmation = confirmation_dialog(self, "Update Available", "A new version of the application is available. Do you want to update now?")
            if confirmation == QMessageBox.Yes:
                os.startfile("updater.exe")
                QApplication.quit()
        else:
            message = QMessageBox()
            message.setText("No updates available")
            message.exec()
    class AboutDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.version = metadata.VERSION
            self.setWindowTitle("About")
            self.layout = QVBoxLayout()
            self.setLayout(self.layout)

            self.name_label = QLabel("Project Management System")
            self.layout.addWidget(self.name_label)


            self.version_label = QLabel(f"Version: {self.version}" or "Unknown")
            self.layout.addWidget(self.version_label)

            self.created_label = QLabel("_load_creation_date")
            self.layout.addWidget(self.created_label)

            self.release_notes_label = QLabel("_load_release_notes")
            self.layout.addWidget(self.release_notes_label)

            self.button_layout = QHBoxLayout()
            self.layout.addLayout(self.button_layout)

            self.update_button = QPushButton("Update...")
            self.button_layout.addWidget(self.update_button)
            self.update_button.clicked.connect(self.update_button_handler)
            self.cancel_button = QPushButton("CANCEL")
            self.button_layout.addWidget(self.cancel_button)
            self.cancel_button.clicked.connect(self.accept)


            self.refresh_data()
        def refresh_data(self):
            self.name_label.setText(metadata.NAME)
            self.version_label.setText(f"Version: {metadata.VERSION}")
            created_at  = metadata.CREATED_AT
            self.created_label.setText(created_at)
            self.release_notes_label.setText(metadata.RELEASE_NOTES)

        @staticmethod
        def update_button_handler(self):
            check = check_for_updates()
            if check:
                #TODO: When updater will be ready, uncomment this line
                """os.startfile("updater.exe")
                QApplication.quit()"""
                pass
            else:
                message = QMessageBox()
                message.setText("No updates available")
                message.exec()


class AddItem(QDialog):
    save_signal = Signal()
    def __init__(self,project_id, user_id):
        super().__init__()
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

        self.code_label = QLabel("Code: ")
        self.data_layout.addWidget(self.code_label, 1, 0)
        self.code_input = QLineEdit()
        self.data_layout.addWidget(self.code_input, 1, 1)

        self.quantity_label = QLabel("Quantity: ")
        self.data_layout.addWidget(self.quantity_label, 2, 0)
        self.quantity_input = QLineEdit()
        self.data_layout.addWidget(self.quantity_input, 2, 1)
        units = ["mtr", "psc"]
        self.unit_label = QLabel("Unit: ")
        self.data_layout.addWidget(self.unit_label, 3, 0)
        self.unit_dropdown = QComboBox()
        self.unit_dropdown.addItems(units)
        self.data_layout.addWidget(self.unit_dropdown, 3, 1)
        self.unit_dropdown.setCurrentText("mtr")
        self.description_label = QLabel("Description: ")
        self.data_layout.addWidget(self.description_label, 4, 0)
        self.description_input = QTextEdit()
        self.data_layout.addWidget(self.description_input, 4, 1)

        self.setWindowTitle("Add Item")

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)
        self.save_button = QPushButton("Save")
        self.buttons_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)
        self.cancel_button = QPushButton("Cancel")
        self.buttons_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)
    def save_button_handler(self):
        self.name_input.setStyleSheet("")
        self.code_input.setStyleSheet("")
        self.quantity_input.setStyleSheet("")
        self.description_input.setStyleSheet("")
        name = self.name_input.text().strip()
        code = self.code_input.text().strip() or "unknown"
        quantity = self.quantity_input.text().replace(",", ".").strip()
        unit = self.unit_dropdown.currentText()
        description = self.description_input.toPlainText().strip()
        if not name:
            warning = QMessageBox()
            warning.setText("Item name cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.name_input.setStyleSheet("border: 2px solid red;")
            self.name_input.setFocus()
            return
        if not quantity:
            warning = QMessageBox()
            warning.setText("Quantity cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.quantity_input.clear()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        try:
            quantity = float(quantity)
        except ValueError:
            warning = QMessageBox()
            warning.setText("Quantity must be a number")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return


        new_item = {"project_id": self.project_id,
                    'name': name,
                    'code': code,
                    'quantity': quantity,
                    'unit': unit,
                    'description': description}
        response = requests.post("/projects/project/items/new", json=new_item)
        if response.ok:
            self.accept()
            self.save_signal.emit()
class EditItem(QDialog):
    save_signal = Signal()

    def __init__(self,project_id, user_id, item_id):
        super().__init__()
        self.project_id = project_id
        self.user_id = user_id
        self.item_id = item_id
        self.setWindowTitle("Edit Item")


        edited_item: dict = API_CLIENT.get(f"/projects/project/items/{self.item_id}").json()

        item = SimpleNamespace(**edited_item)


        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data_layout = QGridLayout()
        self.layout.addLayout(self.data_layout)

        self.name_label = QLabel("Name: ")
        self.data_layout.addWidget(self.name_label, 0, 0)

        self.name_input = QLineEdit()
        self.name_input.setText(item.name)
        self.data_layout.addWidget(self.name_input, 0, 1)

        self.code_label = QLabel("Code: ")
        self.data_layout.addWidget(self.code_label, 1, 0)

        self.code_input = QLineEdit()
        self.code_input.setText(item.code)
        self.data_layout.addWidget(self.code_input, 1, 1)

        self.quantity_label = QLabel("Quantity: ")
        self.data_layout.addWidget(self.quantity_label, 2, 0)

        self.quantity_input = QLineEdit()
        self.quantity_input.setText(str(item.quantity))
        self.data_layout.addWidget(self.quantity_input, 2, 1)

        self.unit_label = QLabel("Unit: ")
        self.data_layout.addWidget(self.unit_label, 3, 0)

        self.unit_dropdown = QComboBox()
        units = ["mtr", "psc"]
        self.unit_dropdown.addItems(units)
        if item.unit in units:
            self.unit_dropdown.setCurrentText(item.unit)
        else:
            self.unit_dropdown.setCurrentIndex(0)
        self.data_layout.addWidget(self.unit_dropdown, 3, 1)

        self.description_label = QLabel("Description: ")
        self.data_layout.addWidget(self.description_label, 4, 0)
        self.description_input = QTextEdit()
        self.data_layout.addWidget(self.description_input, 4, 1)
        self.description_input.setText(item.description or "")

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.save_button = QPushButton("Save")
        self.button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)

        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self):
        name = self.name_input.text()
        quantity = self.quantity_input.text()
        code = self.code_input.text() or "unknown"
        unit = self.unit_dropdown.currentText()
        if not name:
            warning = QMessageBox()
            warning.setText("Item name cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.name_input.setStyleSheet("border: 2px solid red;")
            self.name_input.setFocus()
            return

        if not quantity:
            warning = QMessageBox()
            warning.setText("Quantity cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.quantity_input.clear()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        try:
            quantity = float(quantity)
        except ValueError:
            warning = QMessageBox()
            warning.setText("Quantity must be a number")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return

        API_CLIENT.patch(f"/projects/project/items/{self.item_id}/update/",
                         json={"name": name,"quantity": quantity,"code": code,"unit": unit})

        self.accept()
        self.save_signal.emit()
class AddActivity(QDialog):
    save_signal = Signal()

    def __init__(self, project_id, user_id):
        super().__init__()
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

        self.quantity_label = QLabel("Time: ")
        self.data_layout.addWidget(self.quantity_label, 1, 0)
        self.quantity_input = QLineEdit()
        self.data_layout.addWidget(self.quantity_input, 1, 1)

        self.description_label = QLabel("Description: ")
        self.data_layout.addWidget(self.description_label, 2, 0)
        self.description_input = QTextEdit()
        self.data_layout.addWidget(self.description_input, 2, 1)

        self.setWindowTitle("Add Activity")

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)
        self.save_button = QPushButton("Save")
        self.buttons_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)
        self.cancel_button = QPushButton("Cancel")
        self.buttons_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self):
        name = self.name_input.text().strip() or None
        time = self.quantity_input.text().strip() or None
        description = self.description_input.toPlainText().strip() or ""
        self.name_input.setStyleSheet("")
        self.quantity_input.setStyleSheet("")
        if not name:
            warning = QMessageBox()
            warning.setText("Activity name cannot be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.name_input.setStyleSheet("border: 2px solid red;")
            self.name_input.setFocus()
            return
        if not time:
            warning = QMessageBox()
            warning.setText("Quantity field can't be empty")
            warning.setWindowTitle("Warning")
            warning.setIcon(QMessageBox.Warning)
            warning.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        try:
            time = float(time.replace(",", "."))
        except ValueError:
            warning = QMessageBox()
            warning.setText("Quantity must be a number")
            warning.setWindowTitle("Warning")
            warning.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        if time <= 0:
            message = QMessageBox()
            message.setText("Quantity value must be greater than zero")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return



        new = ProjectActivitySchema(project_id=self.project_id,
                             name=name,
                             time=time,
                             description=description)
        API_CLIENT.post("/projects/project/activities/new", json=new.model_dump())

        self.save_signal.emit()
        self.accept()
class EditActivity(QDialog):
    save_signal = Signal()

    def __init__(self,project_id, user_id, item_id):
        super().__init__()

        self.project_id = project_id
        self.user_id = user_id
        self.activity_id = item_id
        self.setWindowTitle("Edit Activity")

        edited_activity: dict = API_CLIENT.get(f"/projects/project/activities/{self.activity_id}").json()

        activity = SimpleNamespace(**edited_activity)


        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data_layout = QGridLayout()
        self.layout.addLayout(self.data_layout)

        self.name_label = QLabel("Name: ")
        self.data_layout.addWidget(self.name_label, 0, 0)

        self.name_input = QLineEdit()
        self.name_input.setText(activity.name)
        self.data_layout.addWidget(self.name_input, 0, 1)


        self.quantity_label = QLabel("Time: ")
        self.data_layout.addWidget(self.quantity_label, 1, 0)

        self.quantity_input = QLineEdit()
        self.quantity_input.setText(str(activity.time))
        self.data_layout.addWidget(self.quantity_input, 1, 1)

        self.description_label = QLabel("Description: ")
        self.data_layout.addWidget(self.description_label, 2, 0)
        self.description_input = QTextEdit()
        self.data_layout.addWidget(self.description_input, 2, 1)
        self.description_input.setText(activity.description)


        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.save_button = QPushButton("Save")
        self.button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)

        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self):
        name = self.name_input.text().strip()
        time = self.quantity_input.text().strip().replace(",", ".")
        description = self.description_input.toPlainText().strip()

        self.quantity_input.setStyleSheet("")
        self.name_input.setStyleSheet("")


        if not name:
            message = QMessageBox()
            message.setText("Please enter a name")
            message.exec()
            self.name_input.setStyleSheet("border: 2px solid red;")
            self.name_input.setFocus()
            return
        if not time:
            message = QMessageBox()
            message.setText(f"Please enter a quantity")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        try:
            time = float(time)
        except ValueError:
            message = QMessageBox()
            message.setText("Please enter a number")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        if time <= 0:
            message = QMessageBox()
            message.setText("Quantity value must be greater than zero")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return


        API_CLIENT.patch(f"/projects/project/activities/{self.activity_id}/update/", json={
            "name": name,
            "time": time,
            "description": description
        })
        print(f"Activity {self.activity_id} updated")
        self.accept()
        self.save_signal.emit()
class AddToDo(QDialog):
    save_signal = Signal()

    def __init__(self,project_id, user_id):
        super().__init__()

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

        self.quantity_label = QLabel("Time: ")
        self.data_layout.addWidget(self.quantity_label, 1, 0)
        self.quantity_input = QLineEdit()
        self.data_layout.addWidget(self.quantity_input, 1, 1)

        self.description_label = QLabel("Description: ")
        self.data_layout.addWidget(self.description_label, 2, 0)
        self.description_input = QTextEdit()
        self.data_layout.addWidget(self.description_input, 2, 1)

        self.setWindowTitle("Add Todo")

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)
        self.save_button = QPushButton("Save")
        self.buttons_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)
        self.cancel_button = QPushButton("Cancel")
        self.buttons_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self):
        todo = self.name_input.text().strip()
        time = self.quantity_input.text().strip().replace(",", ".")

        self.quantity_input.setStyleSheet("")
        self.name_input.setStyleSheet("")

        if not todo:
            message = QMessageBox()
            message.setText("Please enter a name")
            message.exec()
            self.name_input.setStyleSheet("border: 2px solid red;")
            self.name_input.setFocus()
            return
        if not time:
            message = QMessageBox()
            message.setText(f"Please enter a quantity")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        try:
            time = float(time.replace(",", "."))
        except ValueError:
            message = QMessageBox()
            message.setText("Please enter a number")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        if time <= 0:
            message = QMessageBox()
            message.setText("Time value must be greater than zero")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return


        todo = self.name_input.text().strip()
        time = self.quantity_input.text().strip().replace(",", ".")
        description = self.description_input.toPlainText().strip() or ""
        new_todo = ProjectActivitySchema(name=todo,
                                         time=float(time),
                                         description=description,
                                         project_id=self.project_id)
        API_CLIENT.post("projects/project/todos/new", json=new_todo.model_dump())
        self.accept()
        self.save_signal.emit()
class EditToDo(QDialog):
    save_signal = Signal()

    def __init__(self,project_id, user_id, todo_id):
        super().__init__()

        self.project_id = project_id
        self.user_id = user_id
        self.todo_id = todo_id
        self.setWindowTitle("Edit Item")

        fetched_todo = API_CLIENT.get(f"/projects/project/todos/{self.todo_id}").json()
        todo = SimpleNamespace(**fetched_todo)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data_layout = QGridLayout()
        self.layout.addLayout(self.data_layout)

        self.name_label = QLabel("Name: ")
        self.data_layout.addWidget(self.name_label, 0, 0)

        self.name_input = QLineEdit()
        self.name_input.setText(todo.name)
        self.data_layout.addWidget(self.name_input, 0, 1)

        self.quantity_label = QLabel("Quantity: ")
        self.data_layout.addWidget(self.quantity_label, 1, 0)

        self.quantity_input = QLineEdit()
        self.quantity_input.setText(str(todo.time))
        self.data_layout.addWidget(self.quantity_input, 1, 1)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.save_button = QPushButton("Save")
        self.button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_button_handler)

        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)

    def save_button_handler(self):
        name = self.name_input.text().strip()
        time = self.quantity_input.text().strip().replace(",", ".")

        self.quantity_input.setStyleSheet("")
        self.name_input.setStyleSheet("")

        if not name:
            message = QMessageBox()
            message.setText("Please enter a name")
            message.exec()
            self.name_input.setStyleSheet("border: 2px solid red;")
            self.name_input.setFocus()
            return
        if not time:
            message = QMessageBox()
            message.setText(f"Please enter a quantity")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        try:
            time = float(time.replace(",", "."))
        except ValueError:
            message = QMessageBox()
            message.setText("Please enter a number")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return
        if time <= 0:
            message = QMessageBox()
            message.setText("Quantity value must be greater than zero")
            message.exec()
            self.quantity_input.setStyleSheet("border: 2px solid red;")
            self.quantity_input.setFocus()
            return

        API_CLIENT.patch(f"/projects/project/todos/{self.todo_id}/update/",
                         json={"name": name,
                                "time": time,
                                "project_id": self.project_id})
        self.accept()
        self.save_signal.emit()
class CustomPushButton(QPushButton):
    # Added "Enter" key press event to the button"
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        # "Enter" as default trigger key
    def keyPressEvent(self,event):
        if event.key() == 16777220:
            self.clicked.emit()
            return
        super().keyPressEvent(event)
class EraseServiceProjectConfirmationDialog(QDialog):
    def __init__(self, database, project_id, user_id):
        super().__init__()
        self.database = database
        self.project_id = project_id
        self.user_id = user_id
        self.setWindowTitle("Confirm Erase")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel("Are you sure you want to erase this project?")
        self.inputs_layout = QGridLayout()
class Label(QLabel):
    # Custom label with set Context Menu Policy
    def __init__(self, *args, context_menu=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.context_menu = context_menu
        if context_menu:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(
                lambda qpoint, label=self: label.context_menu.exec(label.mapToGlobal(qpoint))
            )




        


        




























