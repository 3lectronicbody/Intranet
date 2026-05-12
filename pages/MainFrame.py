from PySide6.QtWidgets import QStackedWidget, QGraphicsBlurEffect

from pages.login_page import LoginPage
from pages.main_menu_page import MainMenuPage
from pages.projects_page import ProjectsPage
from pages.sign_up_page import SignUpPage
from pages.project.ProjectWindow import ProjectPage
from pages.create_project_page import CreateProjectPage
from pages.employees_page import EmployeesPage

class MainFrame(QStackedWidget):
    def __init__(self, database=None):
        super().__init__()

        self.user_id = None
        self.project_id = None
        self.database = database

        self.project_window = None




        self.setMaximumSize(800, 1000)


        self.login_page = LoginPage(self.database)
        self.login_page.login_signal.connect(self.show_main_menu_page)
        self.login_page.close_signal.connect(self.close)
        self.login_page.sign_up_signal.connect(self.show_sign_up_page)

        self.login_page_size = None

        self.main_menu_page = MainMenuPage(self.database)
        self.main_menu_page.logout_signal.connect(self.show_login_page)
        self.main_menu_page.projects_signal.connect(self.show_projects_page)
        self.main_menu_page.employees_signal.connect(self.show_employees_page)


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




        self.addWidget(self.login_page)
        self.addWidget(self.main_menu_page)
        self.addWidget(self.sign_up_page)
        self.addWidget(self.projects_page)
        self.addWidget(self.create_project_page)
        self.addWidget(self.employees_page)

        self.show_login_page()




    def show_main_menu_page(self, user_id = None):
        self.setWindowTitle("Main Menu")
        # If an ID is provided (from Login), save it!
        if user_id is not None:
            self.user_id = user_id
        self.main_menu_page.load_user(self.user_id)

        self.setCurrentWidget(self.main_menu_page)
    def show_login_page(self):
        self.setWindowTitle("Login")
        self.user_id = None
        self.setCurrentWidget(self.login_page)
    def show_sign_up_page(self):
        self.setWindowTitle("Sign Up")
        self.setCurrentWidget(self.sign_up_page)
    def show_projects_page(self):
        self.setWindowTitle("Projects")
        self.projects_page.load_user(self.user_id)
        self.projects_page.refresh_data()
        self.setCurrentWidget(self.projects_page)
    def show_create_project_page(self):
        self.setWindowTitle("Create Project")
        self.create_project_page.load_user(self.user_id)
        self.setCurrentWidget(self.create_project_page)
    def show_project_page(self, project_id):
        self.project_window = ProjectPage(self.database, project_id=project_id, user_id=self.user_id)
        blur_effect = QGraphicsBlurEffect(self)
        blur_effect.setBlurRadius(10)
        self.projects_page.setGraphicsEffect(blur_effect)


        self.project_window.exec()

        self.projects_page.refresh_data()
        self.projects_page.setGraphicsEffect(None)

    def show_employees_page(self):
        self.setWindowTitle("Employees")
        self.employees_page.load_user(self.user_id)
        self.employees_page.refresh_data()
        self.setCurrentWidget(self.employees_page)


