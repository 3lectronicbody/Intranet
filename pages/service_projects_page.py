from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QComboBox, QLabel, QHBoxLayout, QLineEdit, QPushButton
from database.models import ServiceProjects
from helper_functions import clear_layout
from custom_widgets_folder.custom_widgets import CreateServiceProject, EditServiceProject
from custom_widgets_folder.ServiceProjectDialog import ServiceProjectDialog
from datetime import datetime


class ServiceProjectsPage(QWidget):
    back_signal = Signal()
    def __init__(self, database,user_id,parent=None):
        super().__init__(parent)

        self.database = database
        self.user_id = user_id
        self.parent = parent
        self.dialog = None


        # default sorting conditions
        self.sort_header = 'number'
        self.sort_mode = "asc"

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.dropdown_service_projects = QComboBox()
        # self.dropdown_service_projects.setView(QListView())

        self.options = [ "All", "Active", "Complete",]
        self.dropdown_service_projects.addItems(self.options)
        self.dropdown_service_projects.setCurrentIndex(0)
        self.dropdown_service_projects.currentTextChanged.connect(self.dropdown_change_handler)
        self.main_layout.addWidget(self.dropdown_service_projects)

        self.search_bar_layout = QHBoxLayout()
        self.main_layout.addLayout(self.search_bar_layout)
        self.search_label = QLabel("Search:")
        self.search_bar_layout.addWidget(self.search_label)
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.searchbar_change_handler)
        self.search_bar_layout.addWidget(self.search_input)

        self.data_layout = QGridLayout()
        self.main_layout.addLayout(self.data_layout)

        self.main_layout.addStretch(1)

        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        self.create_button = QPushButton("CREATE PROJECT")
        self.create_button.setStyleSheet("color: green;")
        self.button_layout.addWidget(self.create_button)
        self.create_button.clicked.connect(self.create_project_button_handler)
        self.cancel_button = QPushButton("BACK")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_button_handler)

        self.refresh_data()

    def refresh_data(self):
        clear_layout(self.data_layout, grid_layout=True)

        # HEADER
        headers =[]
        number_header = QPushButton("Number",flat=True)
        number_header.clicked.connect(self.number_header_clicked)
        headers.append(number_header)
        self.data_layout.addWidget(number_header, 0, 0)
        owner_header = QPushButton("Owner", flat=True)
        owner_header.clicked.connect(self.owner_header_clicked)
        headers.append(owner_header)
        self.data_layout.addWidget(owner_header, 0, 1)
        item_header = QPushButton("Item", flat=True)
        item_header.clicked.connect(self.item_header_clicked)
        headers.append(item_header)
        self.data_layout.addWidget(item_header, 0, 2)
        start_date_header = QPushButton("Start Date", flat=True)
        start_date_header.clicked.connect(self.start_date_header_clicked)
        headers.append(start_date_header)
        self.data_layout.addWidget(start_date_header, 0, 3)
        end_date_header = QPushButton("End Date", flat=True)
        end_date_header.clicked.connect(self.end_date_header_clicked)
        headers.append(end_date_header)
        self.data_layout.addWidget(end_date_header, 0, 4)
        for header in headers:
            header.setStyleSheet("font-weight: bold;")

        with self.database.session() as session:

            selected_filter = self.dropdown_service_projects.currentText()
            searched_text = self.search_input.text().strip().lower()
            if selected_filter == "All":
                projects = session.query(ServiceProjects).all()
            elif selected_filter == "Active":
                projects = session.query(ServiceProjects).filter_by(active=True).all()
            elif selected_filter == "Complete":
                projects = session.query(ServiceProjects).filter_by(active=False).all()

            projects = [project for project in projects if searched_text in
                        project.owner.lower() or searched_text in str(project.number).lower() or
                        searched_text in project.manufacturer.lower() or searched_text in project.model.lower()]
            if self.sort_header == "number":
                if self.sort_mode == "asc":
                    projects.sort(key=lambda x: x.number, reverse=False)
                else:
                    projects.sort(key=lambda x: x.number, reverse=True)

            elif self.sort_header == "owner":
                if self.sort_mode == "asc":
                    projects.sort(key=lambda x: x.owner, reverse=False)
                else:
                    projects.sort(key=lambda x: x.owner, reverse=True)

            elif self.sort_header == "item":
                if self.sort_mode == "asc":
                    projects.sort(key=lambda x: x.manufacturer + " " + x.model, reverse=False)
                else:
                    projects.sort(key=lambda x: x.manufacturer + " " + x.model, reverse=True)

            elif self.sort_header == "start_date":
                if self.sort_mode == "asc":
                    projects.sort(key=lambda x: x.start_date, reverse=False)
                else:
                    projects.sort(key=lambda x: x.start_date, reverse=True)

            elif self.sort_header == "end_date":
                if self.sort_mode == "asc":
                    projects.sort(key=lambda x:
                    (x.end_date if x.end_date is not None else datetime(9999,12,1)), reverse=False)

                else:
                    projects.sort(key=lambda x:
                    (x.end_date if x.end_date is not None else datetime(9999, 12, 1)), reverse=True)


            # no projects label
            if not projects:
                no_projects_label = QLabel("No projects found")
                self.data_layout.addWidget(no_projects_label, 1, 0, 1, 5)
                no_projects_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # data load
            for index, project in enumerate(projects, start=1):

                # NUMBER LABEL
                number_label = QLabel(str(project.number))
                number_label.setStyleSheet("font-weight: bold;")
                # number label tooltip
                if project.service_parts:
                    service_parts = ""
                    for part in project.service_parts:
                        service_parts += (f"Name: {part['name']}<br>"
                                          f"Code: {part['code']}<br>"
                                          f"Quantity: {part['quantity']}<br>")
                else:
                    service_parts = "No service parts"

                if project.tasks:
                    tasks = ""
                    for task in project.tasks:
                        tasks += f"{task['task_name']} -> {task['task_time']} hours<br>"
                else:
                    tasks = "No tasks"


                tooltip_content = (
                    f"<b>Code:</b> {project.code}<br>"
                    f"<b>Serial Number:</b> {project.serial_number}<br>"
                    f"<b>Description:</b> {project.description}<br><br>"
                    f"<b>SERVICE PARTS:</b><br> {service_parts}<br><br>"
                    f"<b>TASKS:</b><br> {tasks}<br>"

                )
                number_label.setToolTip(tooltip_content)
                self.data_layout.addWidget(number_label, index, 0)
                # OWNER LABEL
                owner_label = QLabel(project.owner)
                tooltip_content = f"Phone: {project.phone_number}\nEmail: {project.email}"
                owner_label.setToolTip(tooltip_content)
                self.data_layout.addWidget(owner_label, index, 1)
                # DEVICE LABEL
                item = project.manufacturer + " " + project.model
                item_label = QLabel(item)
                self.data_layout.addWidget(item_label, index, 2)
                # START DATE LABEL
                start_date_label = QLabel(project.start_date.strftime("%d/%m/%Y"))
                self.data_layout.addWidget(start_date_label, index, 3)
                # END DATE LABEL
                if project.end_date:
                    end_date_label = QLabel(project.end_date.strftime("%d/%m/%Y"))
                    end_date_label.setStyleSheet("font-weight: bold;")
                else:
                    end_date_label = QLabel("Pending...")
                    end_date_label.setStyleSheet("color: green;")
                self.data_layout.addWidget(end_date_label, index, 4)
                # EDIT BUTTON
                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda _,project_id=project.id: self.edit_project_button_handler(project_id))
                self.data_layout.addWidget(edit_button, index, 5)
                # OPEN BUTTON
                open_button = QPushButton("Open")
                self.data_layout.addWidget(open_button, index, 6)
                if not project.active:
                    open_button.setDisabled(True)
                    open_button.setFlat(True)
                open_button.clicked.connect(lambda _,project_id=project.id: self.open_project_button_handler(project_id))


    # Main Window
    def dropdown_change_handler(self):
        self.refresh_data()
    def searchbar_change_handler(self):
        self.refresh_data()
    def create_project_button_handler(self):
        self.dialog = CreateServiceProject(self.database, self.user_id)
        self.dialog.save_signal.connect(self.refresh_data)
        self.dialog.exec()
    def cancel_button_handler(self):
        self.back_signal.emit()
    # Single Service project buttons
    def edit_project_button_handler(self, project_id):
        # Edit service project
        self.dialog = EditServiceProject(self.database, self.user_id, project_id)
        self.dialog.save_signal.connect(self.refresh_data)
        self.dialog.exec()

    def open_project_button_handler(self, project_id):

        service_project = ServiceProjectDialog(self.database, self.user_id, project_id)
        service_project.refresh_signal.connect(self.refresh_data)
        service_project.exec()

    # Headers sorting functions
    def number_header_clicked(self):
        if self.sort_header == "number":
            self.sort_mode = 'desc' if self.sort_mode == 'asc' else 'asc'
        else:
            self.sort_header = 'number'
            self.sort_mode = 'asc'
        self.refresh_data()
    def owner_header_clicked(self):
        if self.sort_header == "owner":
            self.sort_mode = 'desc' if self.sort_mode == 'asc' else 'asc'
        else:
            self.sort_header = 'owner'
            self.sort_mode = 'asc'
        self.refresh_data()
    def item_header_clicked(self):
        if self.sort_header == "item":
            self.sort_mode = 'desc' if self.sort_mode == 'asc' else 'asc'
        else:
            self.sort_header = 'item'
            self.sort_mode = 'asc'
        self.refresh_data()
    def start_date_header_clicked(self):
        if self.sort_header == "start_date":
            self.sort_mode = 'desc' if self.sort_mode == 'asc' else 'asc'
        else:
            self.sort_header = 'start_date'
            self.sort_mode = 'asc'
        self.refresh_data()
    def end_date_header_clicked(self):
        if self.sort_header == "end_date":
            self.sort_mode = 'desc' if self.sort_mode == 'asc' else 'asc'
        else:
            self.sort_header = 'end_date'
            self.sort_mode = 'asc'
        self.refresh_data()



