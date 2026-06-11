from PySide6.QtGui import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QDialog, QVBoxLayout, QTabWidget, QHBoxLayout, QMessageBox, QMenuBar

from database.models import Projects
from pages.project.tabs import ItemsTab, ActivitiesTab, ToDoTab
from custom_widgets import AddItemActivity, ProjectWindowMenuBar
from helper_functions import confirmation_dialog


class ProjectPage(QDialog):
    def __init__(self, database, project_id=None, user_id=None):
        super().__init__()

        self.setMinimumSize(600, 500)

        self.database = database
        self.project_id = project_id
        self.user_id = user_id
        self.add_item_activity_dialog = None

        with self.database.session() as session:
            project = session.query(Projects).get(project_id)
            self.project_name = project.name
            self.project_description = project.description
        self.setWindowTitle(self.project_name)


        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.menu_bar = ProjectWindowMenuBar(self, self.database, self.project_id, self.user_id)
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

        self.items_tab = ItemsTab(self.database, self.project_id, self.user_id)
        self.tab.addTab(self.items_tab, "ITEMS")
        self.items_tab.setObjectName("items_tab")

        self.activities_tab = ActivitiesTab(self.database, self.project_id, self.user_id)
        self.tab.addTab(self.activities_tab, "ACTIVITIES")

        self.todo_tab = ToDoTab(self.database, self.project_id, self.user_id)
        self.tab.addTab(self.todo_tab, "TODO")


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

    def add_button_handler(self):
        current_tab_index = self.tab.currentIndex()

        # 1. Determine the flag
        if current_tab_index == 0:
            flag = "item"
            triggerred_function = self.items_tab.load_data
        elif current_tab_index == 1:
            flag = "activity"
            triggerred_function = self.activities_tab.load_data
        elif current_tab_index == 2:
            flag = "todo"
            triggerred_function = self.todo_tab.load_data
        else:
            return

        # 2. Create the dialog once
        self.add_item_activity_dialog = AddItemActivity(
            self.database, self.project_id, self.user_id, flag=flag
        )

        # 3. Connect the signal to the correct slot
        self.add_item_activity_dialog.save_signal.connect(triggerred_function)

        # 4. Run the dialog once
        self.add_item_activity_dialog.exec()
    def back_button_handler(self, event=None):
        text = "Are you sure you want to leave?"
        dialog = confirmation_dialog(self, title="Confirmation", message=text)
        if dialog == QMessageBox.Yes:
            self.accept()
        else:
            if event:
                event.ignore()

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
    def refresh_data(self):
        # For later use if main project window changes (for example name of the project changed in child dialog)
        pass

    def closeEvent(self, event, /):
        text = "Are you sure you want to leave?"
        dialog = confirmation_dialog(self, title="Confirmation", message=text)
        if dialog == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()








