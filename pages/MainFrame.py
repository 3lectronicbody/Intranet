from PySide6.QtWidgets import QStackedWidget, QMainWindow, QMessageBox, QWidget, QVBoxLayout

from pages.login_page import LoginPage
from pages.main_menu_page import MainMenuPage
from pages.projects_page import ProjectsPage
from pages.sign_up_page import SignUpPage
from pages.project.ProjectWindow import ProjectPage
from pages.create_project_page import CreateProjectPage
from pages.employees_page import EmployeesPage
from pages.service_projects_page import ServiceProjectsPage
from helper_functions import confirmation_dialog

from custom_widgets import MenuBar

class MainFrame(QMainWindow):
    def __init__(self, database=None):
        super().__init__()

        self.user_id = None
        self.project_id = None
        self.database = database

        self.project_window = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.menu_bar = MenuBar(self,self.database, self.project_id, self.user_id, flag="main")
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.menu_bar)


        self.setMaximumSize(800, 1000)

        self.frame = QStackedWidget()
        self.main_layout.addWidget(self.frame)


        self.login_page = LoginPage(self.database)
        self.login_page.login_signal.connect(self.show_main_menu_page)
        self.login_page.close_signal.connect(self.close)
        self.login_page.sign_up_signal.connect(self.show_sign_up_page)

        self.login_page_size = None

        self.main_menu_page = MainMenuPage(self.database)
        self.main_menu_page.logout_signal.connect(self.show_login_page)
        self.main_menu_page.projects_signal.connect(self.show_projects_page)
        self.main_menu_page.employees_signal.connect(self.show_employees_page)
        self.main_menu_page.service_projects_signal.connect(self.show_service_projects_page)


        self.sign_up_page = SignUpPage(self.database)
        self.sign_up_page.cancel_signal.connect(self.show_login_page)
        self.sign_up_page.create_signal.connect(self.show_login_page)

        self.projects_page = ProjectsPage(self.database)
        self.projects_page.back_signal.connect(self.show_main_menu_page)
        self.projects_page.create_signal.connect(self.show_create_project_page)
        self.projects_page.open_signal.connect(self.show_project_page) # Signal takes project_id

        self.create_project_page = CreateProjectPage(self.database)
        self.create_project_page.cancel_signal.connect(self.show_projects_page)
        self.create_project_page.create_signal.connect(self.show_projects_page)

        self.employees_page = EmployeesPage(self.database)
        self.employees_page.back_signal.connect(self.show_main_menu_page)

        self.service_projects_page = ServiceProjectsPage(self.database)
        self.service_projects_page.back_signal.connect(self.show_main_menu_page)






        self.frame.addWidget(self.login_page)
        self.frame.addWidget(self.main_menu_page)
        self.frame.addWidget(self.sign_up_page)
        self.frame.addWidget(self.projects_page)
        self.frame.addWidget(self.create_project_page)
        self.frame.addWidget(self.employees_page)
        self.frame.addWidget(self.service_projects_page)

        self.show_login_page()


    def show_main_menu_page(self, user_id = None):
        self.setWindowTitle("Main Menu")
        # If an ID is provided (from Login), save it!
        if user_id is not None:
            self.user_id = user_id
        self.main_menu_page.load_user(self.user_id)

        self.frame.setCurrentWidget(self.main_menu_page)
    def show_login_page(self):
        self.setWindowTitle("Login")
        self.user_id = None
        self.frame.setCurrentWidget(self.login_page)
    def show_sign_up_page(self):
        self.setWindowTitle("Sign Up")
        self.frame.setCurrentWidget(self.sign_up_page)
    def show_projects_page(self):
        self.setWindowTitle("Projects")
        self.projects_page.load_user(self.user_id)
        self.projects_page.refresh_data()
        self.frame.setCurrentWidget(self.projects_page)
    def show_create_project_page(self):
        self.setWindowTitle("Create Project")
        self.create_project_page.load_user(self.user_id)
        self.frame.setCurrentWidget(self.create_project_page)
    def show_project_page(self, project_id):
        self.hide()
        self.project_window = ProjectPage(self.database, project_id=project_id, user_id=self.user_id)
        """blur_effect = QGraphicsBlurEffect(self)
        blur_effect.setBlurRadius(10)
        self.projects_page.setGraphicsEffect(blur_effect)"""


        self.project_window.exec()

        self.projects_page.refresh_data()
        self.show()
        # self.projects_page.setGraphicsEffect(None)
    def show_employees_page(self):
        self.setWindowTitle("Employees")
        self.employees_page.load_user(self.user_id)
        self.employees_page.refresh_data()
        self.frame.setCurrentWidget(self.employees_page)
    def show_service_projects_page(self):
        self.setWindowTitle("Service Projects")
        self.service_projects_page.refresh_data()
        self.frame.setCurrentWidget(self.service_projects_page)

    def closeEvent(self, event, /):
        dialog = confirmation_dialog(self, title="Exit", message="Are you sure you want to exit?")
        if dialog == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()





