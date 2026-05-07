from PySide6.QtGui import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QDialog, QVBoxLayout, QTabWidget

from database.models import Projects


class ProjectPage(QDialog):
    def __init__(self, database, project_id=None, user_id=None):
        super().__init__()

        self.setMinimumSize(600, 500)

        self.database = database
        self.project_id = project_id
        self.user_id = user_id

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
        self.tab.addTab(self.load_general_tab(), "GENERAL")
        self.tab.addTab(QLabel(), "ITEMS")
        self.tab.addTab(QLabel(), "ACTIVITIES")

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



        self.back_button = QPushButton("Back")
        self.main_layout.addWidget(self.back_button)
        self.back_button.clicked.connect(lambda: self.close())







