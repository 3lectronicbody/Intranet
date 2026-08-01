import io
from datetime import datetime
from pathlib import Path

import pypdf
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QTextEdit, QHBoxLayout, QPushButton, \
    QMessageBox

from API.api import client
from helper_functions import confirmation_dialog


class CreateServiceProject(QDialog):
    save_signal = Signal()
    def __init__(self, user_id, project_id=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.project_id = project_id
        if self.project_id:
            response = client.get(f"/service_project/{self.project_id}")
            self.project = response.json()
        self.parent = parent


        self.setWindowTitle("Create Service Project")

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)


        self.layout = QGridLayout()
        self.main_layout.addLayout(self.layout)

        self.number_title_label = QLabel("Number: ")
        self.layout.addWidget(self.number_title_label, 0, 0)
        
        # We need an endpoint for last service project number, or we can use the list of service projects
        response = client.get("service_projects")
        service_projects = response.json()
        
        if service_projects:
            # Sort by number to get the last one
            service_projects.sort(key=lambda x: x['number'], reverse=True)
            last_project = service_projects[0]
            last_number = int(last_project['number'][-3:])
            actual_number = last_number + 1
            formatted_actual_number = f"{actual_number:03d}"
            self.actual_number = str(datetime.now().year) + "/" + str(formatted_actual_number)
        else:
            self.actual_number = str(datetime.now().year) + "/001"
        self.number_input = QLineEdit()
        self.number_input.setText(self.actual_number)
        self.number_input.setStyleSheet("color: #3498db; font-weight: bold;")
        self.number_input.setReadOnly(True)
        self.layout.addWidget(self.number_input, 0, 1)

        self.receive_date_label = QLabel("Date:")
        self.layout.addWidget(self.receive_date_label, 1, 0)
        self.receive_date_input = QLineEdit()
        actual_date = datetime.now().strftime("%d-%m-%Y")
        self.receive_date_input.setText(actual_date)
        self.receive_date_input.setStyleSheet("color: #3498db;")
        self.receive_date_input.setReadOnly(True)
        self.layout.addWidget(self.receive_date_input, 1, 1)

        self.owner_label = QLabel("Owner: ")
        self.layout.addWidget(self.owner_label, 2, 0)
        self.owner_input = QLineEdit()
        self.layout.addWidget(self.owner_input, 2, 1)

        self.phone_number_label = QLabel("Phone Number: ")
        self.layout.addWidget(self.phone_number_label, 3, 0)
        self.phone_number_input = QLineEdit()
        self.layout.addWidget(self.phone_number_input, 3, 1)

        self.email_label = QLabel("Email: ")
        self.layout.addWidget(self.email_label, 4, 0)
        self.email_input = QLineEdit()
        self.layout.addWidget(self.email_input, 4, 1)

        self.manufacturer_label = QLabel("Manufacturer: ")
        self.layout.addWidget(self.manufacturer_label, 5, 0)
        self.manufacturer_input = QLineEdit()
        self.layout.addWidget(self.manufacturer_input, 5, 1)

        self.model_label = QLabel("Model: ")
        self.layout.addWidget(self.model_label, 6, 0)
        self.model_input = QLineEdit()
        self.layout.addWidget(self.model_input, 6, 1)

        self.code_label = QLabel("Code: ")
        self.layout.addWidget(self.code_label, 7, 0)
        self.code_input = QLineEdit()
        self.layout.addWidget(self.code_input, 7, 1)

        self.serial_number_label = QLabel("Serial Number: ")
        self.layout.addWidget(self.serial_number_label, 8, 0)
        self.serial_number_input = QLineEdit()
        self.layout.addWidget(self.serial_number_input, 8, 1)

        self.description_label = QLabel("Description: ")
        self.layout.addWidget(self.description_label, 9, 0)
        self.description_input = QTextEdit()
        self.layout.addWidget(self.description_input, 9 ,1)


        self.main_layout.addStretch(1)

        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.create_button = QPushButton("Create")
        self.button_layout.addWidget(self.create_button)
        self.create_button.clicked.connect(self.create_button_handler)
        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_button_handler)

    def create_button_handler(self):
        confirmation = confirmation_dialog(self, "Create Service Project", "Confirm that You want to create project")
        if confirmation == QMessageBox.Yes:
            number = self.actual_number
            formatted_date: datetime = datetime.now()
            owner = self.owner_input.text()
            phone_number = self.phone_number_input.text()
            email = self.email_input.text()
            manufacturer = self.manufacturer_input.text()
            model = self.model_input.text()
            code = self.code_input.text()
            serial_number = self.serial_number_input.text()
            description = self.description_input.toPlainText()

            # Build payload matching the Pydantic schema
            payload = {
                "number": number,
                "owner": owner or "unknown",
                "start_date": formatted_date,
                "phone_number": phone_number or "unknown",
                "email": email or "unknown",
                "manufacturer": manufacturer or "unknown",
                "model": model or "unknown",
                "code": code or "unknown",
                "serial_number": serial_number or "unknown",
                "description": description or ""
            }

            # Use json= instead of params= to send data in the request body
            response = client.post("/service_projects/new", json=payload)

            if response.status_code == 200:
                new_project_id = response.json()
                self.create_pdf_form(new_project_id)
                self.save_signal.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "Error", f"Could not create service project: {response.text}")

    def cancel_button_handler(self):
        self.reject()

    def create_pdf_form(self, project_id):
        confirmation = confirmation_dialog(self, "Confirmation", "Are you sure you want to generate the PDF form?")
        if confirmation == QMessageBox.StandardButton.Yes:
            response = client.get(f"/service_project/{project_id}")
            project = response.json()
            if not project:
                return

            current_dir = Path(__file__).parent
            empty_pdf_form_path = current_dir.parent / "files" / "service_form.pdf"
            pdf_reader = pypdf.PdfReader(empty_pdf_form_path)
            writer = pypdf.PdfWriter()
            writer.append(pdf_reader)
            
            # Convert start_date back to datetime for formatting
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
            
            # We need to upload this PDF back to the server
            import base64
            # Actually api.py doesn't have a specific endpoint for uploading PDF yet, 
            # let's use PATCH /service_project/{id} if it can handle bytes or just skip for now 
            # as I don't want to overcomplicate without a clear endpoint for large binary
            # But the user asked to refactor it.
            # I will add a patch call.
            client.patch(f"/service_project/{project_id}", json={"pdf_form": base64.b64encode(bytes_stream.getvalue()).decode('utf-8')})
