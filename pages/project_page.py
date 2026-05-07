from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton
from PySide6.QtCore import Signal
from database.models import Projects


class ProjectPage(QWidget):
    back_signal = Signal(int)
    def __init__(self, database, project_id=None, user_id=None):
        super().__init__()
        self.database = database
        self.project_id = project_id
        self.user_id = user_id

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.label = QLabel(f"__load__")
        self.main_layout.addWidget(self.label, 0, 0)

        self.main_layout.setRowStretch(1,1)

        self.back_button = QPushButton("Back")
        self.main_layout.addWidget(self.back_button, 2, 0)
        self.back_button.clicked.connect(lambda: self.back_signal.emit(self.user_id))


    def load_project(self, project_id, user_id):
        with self.database.session() as session:
            project = session.query(Projects).get(project_id)
            if project is None:
                return
        self.project_id = project_id
        self.user_id = user_id

        self.label.setText(f"PROJECT: {project.name.upper()}")
        self.label.setStyleSheet(f"font-size: 24px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignCenter)
