from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QComboBox, QLabel, QHBoxLayout, QLineEdit, QPushButton
from database.models import ServiceProjects
from helper_functions import clear_layout


class ServiceProjectsPage(QWidget):
    back_signal = Signal()
    def __init__(self, database,parent=None):
        super().__init__(parent)

        self.database = database
        self.parent = parent

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.dropdown_service_projects = QComboBox()
        self.options = [ "all", "active", "complete",]
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
        self.create_button = QPushButton("NEW PROJECT")
        self.create_button.setStyleSheet("color: green;")
        self.button_layout.addWidget(self.create_button)
        self.create_button.clicked.connect(self.create_project_button_handler)
        self.cancel_button = QPushButton("CANCEL")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_button_handler)

        self.refresh_data()

    def refresh_data(self):
        clear_layout(self.data_layout, grid_layout=True)

        with self.database.session() as session:

            selected_filter = self.dropdown_service_projects.currentText()
            searched_text = self.search_input.text().strip()
            if selected_filter == "all":
                projects = session.query(ServiceProjects).all()
            elif selected_filter == "active":
                projects = session.query(ServiceProjects).filter_by(active=True).all()
            elif selected_filter == "complete":
                projects = session.query(ServiceProjects).filter_by(active=False).all()

            projects = [project for project in projects if searched_text in project.owner or searched_text in str(project.number)]

            if not projects:
                no_projects_label = QLabel("No projects found")
                self.data_layout.addWidget(no_projects_label, 0, 0, alignment=Qt.AlignCenter)

            for index, project in enumerate(projects):

                number_label = QLabel(project.owner)
                self.data_layout.addWidget(number_label, index, 0)

                item = project.manufacturer + " " + project.model
                item_label = QLabel(item)
                self.data_layout.addWidget(item_label, index, 1)

    def dropdown_change_handler(self):
        self.refresh_data()
    def searchbar_change_handler(self):
        self.refresh_data()
    def create_project_button_handler(self):
        pass
    def cancel_button_handler(self):
        self.back_signal.emit()





