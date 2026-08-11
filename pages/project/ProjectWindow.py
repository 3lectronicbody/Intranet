import requests
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QDialog, QVBoxLayout, QTabWidget, QHBoxLayout, QMessageBox
from config import API_PATH
from pages.project.tabs import ItemsTab, ActivitiesTab, ToDoTab
from custom_widgets_folder.custom_widgets import AddActivity, AddItem, AddToDo, MenuBar
from helper_functions import confirmation_dialog, project_summary_pdf
from types import SimpleNamespace



class ProjectPage(QDialog):
    def __init__(self,project_id=None, user_id=None):
        super().__init__()

        self.setMinimumSize(600, 500)

        self.project_id = project_id
        self.user_id = user_id
        self.add_activity_dialog = None
        self.add_item_dialog = None
        self.add_todo_dialog = None

        project = requests.get(f"{API_PATH}/projects/{project_id}").json()
        project = SimpleNamespace(**project)


        self.project_name = project.name
        self.project_description = project.description
        self.setWindowTitle(self.project_name)


        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.menu_bar = MenuBar(self, self.user_id, project_id=self.project_id, flag="project")
        self.main_layout.setContentsMargins(0, 0, 0, 1)
        self.main_layout.addWidget(self.menu_bar)

        self.project_name_label = QLabel(f"Project: {self.project_name} ")
        self.main_layout.addWidget(self.project_name_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.tab = QTabWidget()

        # EXPANDING TAB BAR TABS EVENLY
        # 1. Clear any fixed widths you set
        self.tab.tabBar().setExpanding(True)
        self.tab.tabBar().setDocumentMode(True)
        # 2. Use this stylesheet instead
        self.tab.setStyleSheet("""
            QTabBar::tab {
                min-width: 10ex; /* 'ex' scales with the font size */
                padding: 10px;
            }
        """)
        self.tab.setMinimumHeight(300)

        self.main_layout.addWidget(self.tab)

        self.items_tab = ItemsTab(self.project_id, self.user_id)
        self.tab.addTab(self.items_tab, "ITEMS")
        self.items_tab.setObjectName("items_tab")

        self.activities_tab = ActivitiesTab(self.project_id, self.user_id)
        self.tab.addTab(self.activities_tab, "ACTIVITIES")

        self.todo_tab = ToDoTab( self.project_id, self.user_id)
        self.tab.addTab(self.todo_tab, "TODO")

        # COMPLETE PROJECT BUTTON
        self.complete_project_button = QPushButton("Complete Project")
        self.main_layout.addWidget(self.complete_project_button)
        self.complete_project_button.clicked.connect(self.complete_project_button_handler)
        self.complete_project_button.hide()
        # ACTIVATE PROJECT BUTTON (THE SAME PLACE AS COMPLETE BUTTON)
        self.activate_project_button = QPushButton("Activate")
        self.main_layout.addWidget(self.activate_project_button)
        self.activate_project_button.clicked.connect(self.activate_project_button_handler)
        self.activate_project_button.hide()

        # ADD and BACK buttons
        self.buttons_layout = QHBoxLayout()
        self.main_layout.addLayout(self.buttons_layout)


        self.add_button = QPushButton("Add Item")
        self.buttons_layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.add_button_handler)
        self.back_button = QPushButton("Back")
        self.buttons_layout.addWidget(self.back_button)
        self.back_button.clicked.connect(lambda: self.back_button_handler())

        # Changing ADD BUTTON text based on the current tab

        self.tab.currentChanged.connect(self.refresh_tab)
        self.refresh_page()
    def refresh_tab(self):
        # Changing ADD BUTTON text based on the current tab
        # Refreshing data based on change of the current tab
        if self.tab.currentIndex() == 0:
            self.add_button.setText("Add Item")
            self.items_tab.load_data()
        elif self.tab.currentIndex() == 1:
            self.add_button.setText("Add Activity")
            self.activities_tab.load_data()
        elif self.tab.currentIndex() == 2:
            self.add_button.setText("Add To Do")
            self.todo_tab.load_data()
    def refresh_page(self):
        project = requests.get(f"{API_PATH}/projects/{self.project_id}").json()
        if not project['is_active']:
            self.complete_project_button.hide()
            self.activate_project_button.show()
        else:
            self.complete_project_button.show()
            self.activate_project_button.hide()
    def add_button_handler(self):
        current_tab_index = self.tab.currentIndex()

        # 1. Determine the flag
        if current_tab_index == 0:
            self.add_item_dialog = AddItem(self.project_id, self.user_id)
            self.add_item_dialog.save_signal.connect(self.items_tab.load_data)
            self.add_item_dialog.exec()

        elif current_tab_index == 1:
            self.add_activity_dialog = AddActivity(self.project_id, self.user_id)
            self.add_activity_dialog.save_signal.connect(self.activities_tab.load_data)
            self.add_activity_dialog.exec()

        elif current_tab_index == 2:
            self.add_todo_dialog = AddToDo(self.project_id, self.user_id)
            self.add_todo_dialog.save_signal.connect(self.todo_tab.load_data)
            self.add_todo_dialog.exec()
    def back_button_handler(self, event=None):
        text = "Are you sure you want to leave?"
        dialog = confirmation_dialog(self, title="Confirmation", message=text)
        if dialog == QMessageBox.Yes:
            self.accept()
        else:
            if event:
                event.ignore()
    def complete_project_button_handler(self):
        confirmation = confirmation_dialog(self, title="Confirmation", message="Are you sure you want to complete project ?")
        if confirmation == QMessageBox.Yes:
            pdf_summary_confirmation = confirmation_dialog(self, title="Pdf Summary", message="Do You want to create summary file")
            if pdf_summary_confirmation == QMessageBox.Yes:
                pass
                #Todo: create pdf summary file
            # TODO: patch project to complete it -> projec.is_active = False
            self.refresh_page()

        else:
            return
    def activate_project_button_handler(self):
        with self.database.session() as session:
            project = session.get(Projects, self.project_id)
            project.is_active = True
            session.commit()
        self.refresh_page()

    def closeEvent(self, event, /):
        text = "Are you sure you want to leave?"
        dialog = confirmation_dialog(self, title="Confirmation", message=text)
        if dialog == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()








