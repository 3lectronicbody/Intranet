from PySide6.QtWidgets import QApplication
from pages.MainFrame import MainFrame
from database.database import Database
import qt_material
import sys
from helper_functions import load_css




if __name__ == "__main__":
    database = Database()
    app = QApplication(sys.argv)

    # CUSTOM STYLESHEETS
    # 1. Apply the stylesheet QTMATERIAL_THEME
    themes = ['dark_amber.xml',
              'dark_blue.xml',
              'dark_cyan.xml',
              'dark_lightgreen.xml',
              'dark_pink.xml',
              'dark_purple.xml',
              'dark_red.xml',
              'dark_teal.xml',
              'dark_yellow.xml',
              'light_amber.xml',
              'light_blue.xml',
              'light_cyan.xml',
              'light_cyan_500.xml',
              'light_lightgreen.xml',
              'light_pink.xml',
              'light_purple.xml',
              'light_red.xml',
              'light_teal.xml',
              'light_yellow.xml']
    # qt_material.apply_stylesheet(app, theme=themes[7])
    app.setStyle("Fusion")
    # 2. Apply the custom stylesheet
    current_style = app.styleSheet()
    custom_css = load_css(r"C:\Users\Mateusz\PycharmProjects\Intranet\css\app_stylesheet.css")
    app.setStyleSheet(current_style + "\n" + custom_css)


    root = MainFrame(database)
    root.show()

    app.exec()