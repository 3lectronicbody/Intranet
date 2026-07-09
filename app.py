from PySide6.QtWidgets import QApplication
from pages.MainFrame import MainFrame
from database.database import Database
from pathlib import Path
import sys





if __name__ == "__main__":
    database = Database()
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    # 2. Apply the custom_widgets_folder stylesheet
    current_style = app.styleSheet()
    try:
        custom_css = (Path(__file__).parent.resolve() / "css" / "app_stylesheet.css").read_text(encoding="utf-8")

        app.setStyleSheet(current_style + "\n" + custom_css)
    except FileNotFoundError:
        pass


    root = MainFrame(database)
    root.show()

    app.exec()