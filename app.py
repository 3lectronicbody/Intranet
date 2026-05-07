from PySide6.QtWidgets import QApplication
import MainFrame
from database.database import Database
import qt_material
import sys

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


if __name__ == "__main__":
    database = Database()
    app = QApplication(sys.argv)
    qt_material.apply_stylesheet(app, theme=themes[7])

    root = MainFrame.MainFrame(database)
    root.show()

    app.exec()