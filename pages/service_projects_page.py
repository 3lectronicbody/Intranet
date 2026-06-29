from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QComboBox
from database.models import ServiceProjects
from helper_functions import clear_layout


class ServiceProjectsPage(QWidget):
    def __init__(self, database,parent=None):
        super().__init__(parent)

        self.database = database
        self.parent = parent

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.dropdown_service_projects = QComboBox()
        options = [ "all","active", "complete",]
        self.dropdown_service_projects.addItems(options)
        self.dropdown_service_projects.setCurrentIndex(0)

        self.data_layout = QGridLayout()
        self.main_layout.addLayout(self.data_layout)






    def refresh_data(self):
        clear_layout(self.data_layout, grid_layout=True)

        with self.database.session() as session:
            projects = session.query(ServiceProjects).all()
            for index, project in enumerate(projects):




