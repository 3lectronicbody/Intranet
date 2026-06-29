from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout


class ServiceProjectsPage(QWidget):
    def __init__(self, database,parent=None):
        super().__init__(parent)

        self.database = database
        self.parent = parent

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)



    def refresh_data(self):
        pass


