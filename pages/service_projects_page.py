from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QComboBox, QLabel, QHBoxLayout, QLineEdit, QPushButton
from database.models import ServiceProjects
from helper_functions import clear_layout
from custom_widgets import CreateServiceProject
from datetime import datetime


class ServiceProjectsPage(QWidget):
    back_signal = Signal()
    def __init__(self, database,user_id,parent=None):
        super().__init__(parent)

        self.database = database
        self.user_id = user_id
        self.parent = parent
        self.dialog = None

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.dropdown_service_projects = QComboBox()
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
        number_header = QLabel("Number")
        headers.append(number_header)
        self.data_layout.addWidget(number_header, 0, 0)
        owner_header = QLabel("Owner")
        headers.append(owner_header)
        self.data_layout.addWidget(owner_header, 0, 1)
        item_header = QLabel("Item")
        headers.append(item_header)
        self.data_layout.addWidget(item_header, 0, 2)
        start_date_header = QLabel("Start Date")
        headers.append(start_date_header)
        self.data_layout.addWidget(start_date_header, 0, 3)
        end_date_header = QLabel("End Date")
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

            if not projects:
                no_projects_label = QLabel("No projects found")
                self.data_layout.addWidget(no_projects_label, 1, 0, 1, 5)
                no_projects_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


            for index, project in enumerate(projects, start=1):

                number_label = QLabel(str(project.number))
                self.data_layout.addWidget(number_label, index, 0)

                owner_label = QLabel(project.owner)
                self.data_layout.addWidget(owner_label, index, 1)

                item = project.manufacturer + " " + project.model
                item_label = QLabel(item)
                self.data_layout.addWidget(item_label, index, 2)

                start_date_label = QLabel(project.start_date.strftime("%d/%m/%Y"))
                self.data_layout.addWidget(start_date_label, index, 3)

                if project.end_date:
                    end_date_label = QLabel(project.end_date.strftime("%d/%m/%Y"))
                else:
                    end_date_label = QLabel("Pending...")
                self.data_layout.addWidget(end_date_label, index, 4)

                details_button = QPushButton("Details")
                details_button.clicked.connect(lambda _,project_id=project.id: self.details_project_button_handler(project_id))
                self.data_layout.addWidget(details_button, index, 5)

                edit_button = QPushButton("Edit")
                if not project.active:
                    edit_button.setDisabled(True)
                    edit_button.setFlat(True)
                edit_button.clicked.connect(lambda _,project_id=project.id: self.edit_project_button_handler(project_id))
                self.data_layout.addWidget(edit_button, index, 6)

                complete_button = QPushButton("Complete")
                if not project.active:
                    complete_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                    complete_button.setDisabled(True)
                    complete_button.setFlat(True)

                complete_button.clicked.connect(lambda _,project_id=project.id: self.complete_button_handler(project_id))
                self.data_layout.addWidget(complete_button, index, 7)



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

    def edit_project_button_handler(self, project_id):
        pass
    def details_project_button_handler(self, project_id):
        self.dialog = CreateServiceProject.details(self.database,self.user_id,project_id)
        self.dialog.save_signal.connect(self.refresh_data)
        self.dialog.exec()
    def complete_button_handler(self, project_id):
        with self.database.session() as session:
            project = session.query(ServiceProjects).get(project_id)
            print(project.number)
            project.active = False
            project.end_date = datetime.now()
            session.commit()

        self.refresh_data()



