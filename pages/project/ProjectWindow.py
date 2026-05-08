from PySide6.QtGui import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QDialog, QVBoxLayout, QTabWidget, QHBoxLayout

from database.models import Projects
from pages.project.tabs import ItemsTab, ActivitiesTab
from helper import AddItemActivity


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

        self.label = QLabel(f"Project: {self.project_name} ")
        self.main_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

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

        self.activities_tab = ActivitiesTab(self.database, self.project_id, self.user_id)
        self.tab.addTab(self.activities_tab, "ACTIVITIES")


        # ADD and BACK buttons
        self.buttons_layout = QHBoxLayout()
        self.main_layout.addLayout(self.buttons_layout)


        self.add_button = QPushButton("Add")
        self.buttons_layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.add_button_handler)
        self.back_button = QPushButton("Back")
        self.buttons_layout.addWidget(self.back_button)
        self.back_button.clicked.connect(lambda: self.reject())

    def add_button_handler(self):
        current_tab_index = self.tab.currentIndex()

        # 1. Determine the flag
        if current_tab_index == 0:
            flag = "item"
            target_slot = self.items_tab.load_data
        elif current_tab_index == 1:
            flag = "activity"
            target_slot = self.activities_tab.load_data
        else:
            return

        # 2. Create the dialog once
        self.add_item_activity_dialog = AddItemActivity(
            self.database, self.project_id, self.user_id, flag=flag
        )

        # 3. Connect the signal to the correct slot
        self.add_item_activity_dialog.save_signal.connect(target_slot)

        # 4. Run the dialog once
        self.add_item_activity_dialog.exec()







