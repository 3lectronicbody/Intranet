from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QMessageBox, QGraphicsBlurEffect
from database.models import Projects
from helper_functions import clear_layout, confirmation_dialog


class ProjectsPage(QWidget):
    open_signal = Signal(int)
    delete_signal = Signal(int)
    back_signal = Signal()
    create_signal = Signal()
    def __init__(self, database):
        super().__init__()
        self.user_id = None
        self.database = database
        self.project_id = None
        self.blur_effect = None

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.data_frame = QWidget()
        self.data_layout = QGridLayout()
        self.data_frame.setLayout(self.data_layout)

        self.main_layout.addWidget(self.data_frame, 0, 0, 1, 2)

        self.main_layout.setRowStretch(1, 1)


        self.back_button = QPushButton("Back")
        self.main_layout.addWidget(self.back_button, 2, 0)
        self.back_button.clicked.connect(lambda _:self.back_signal.emit())

        self.create_button = QPushButton("Add Project")
        self.create_button.setStyleSheet("color: green;")
        self.main_layout.addWidget(self.create_button, 2, 1)
        self.create_button.clicked.connect(lambda _:self.create_signal.emit())


    def load_user(self, user_id):
        self.user_id = user_id

    def refresh_data(self):
        clear_layout(self.data_layout, grid_layout=True)
        with self.database.session() as session:
            projects = session.query(Projects).all()
            counter = 1
            title_label_list = []
            title_name_label = QLabel("Name")
            title_label_list.append(title_name_label)
            title_desc_label = QLabel("Description")
            title_label_list.append(title_desc_label)
            title_open_label = QLabel("Open")
            title_open_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label_list.append(title_open_label)
            title_delete_label = QLabel("Delete")
            title_delete_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label_list.append(title_delete_label)
            for title in title_label_list:
                title.setStyleSheet("font-weight: bold;")
            self.data_layout.addWidget(title_name_label, 0, 0)
            self.data_layout.addWidget(title_desc_label, 0, 1)
            self.data_layout.addWidget(title_open_label, 0, 2)
            self.data_layout.addWidget(title_delete_label, 0, 3)
            for project in projects:
                project_name_label = QLabel(project.name)
                project_name_label.setStyleSheet("font-weight: bold;")
                self.data_layout.addWidget(project_name_label, counter, 0)


                original_text = project.description
                first_line = original_text.splitlines()[0]
                project_description_label = QLabel(first_line)
                project_description_label.setWordWrap(False)
                project_description_label.setFixedHeight(project_description_label.fontMetrics().height())
                project_description_label.setStyleSheet("font-style: italic;")
                project_description_label.setToolTip(original_text)
                self.data_layout.addWidget(project_description_label, counter, 1)

                open_project_button = QPushButton("Open")
                open_project_button.setStyleSheet("color: green;")
                self.data_layout.addWidget(open_project_button, counter, 2)
                open_project_button.clicked.connect(lambda _, project_id=project.id: self.open_signal.emit(project_id))

                delete_project_button = QPushButton("Delete")
                delete_project_button.setStyleSheet("color: red;")
                self.data_layout.addWidget(delete_project_button, counter, 3)
                delete_project_button.clicked.connect(lambda _, project_id=project.id: self.delete_button_handler(project_id))
                counter += 1

    def showEvent(self, event, /):
        self.refresh_data()
        super().showEvent(event)
    def delete_button_handler(self, project_id):
        warning = confirmation_dialog(self, title="Warning", message="Are you sure you want to delete this project?")
        if warning == QMessageBox.No:
            return
        with self.database.session() as session:
            project = session.query(Projects).get(project_id)
            session.delete(project)
            session.commit()
            self.refresh_data()


