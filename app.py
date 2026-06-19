from PySide6.QtWidgets import QApplication
from pages.MainFrame import MainFrame
from database.database import Database
from pathlib import Path
import sys
from helper_functions import load_css




if __name__ == "__main__":
    database = Database()
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    # 2. Apply the custom stylesheet
    current_style = app.styleSheet()
    custom_css = (Path(__file__).parent.resolve() / "css" / "app_stylesheet.css").read_text()
    # custom_css = load_css(r"C:\Users\Mateusz\PycharmProjects\Intranet\css\app_stylesheet.css")
    app.setStyleSheet(current_style + "\n" + custom_css)


    root = MainFrame(database)
    root.show()

    app.exec()