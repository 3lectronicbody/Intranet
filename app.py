import subprocess
import requests

from PySide6.QtWidgets import QApplication, QMessageBox
from pages.MainFrame import MainFrame
from pathlib import Path
import sys, os
from helper_functions import check_for_updates,confirmation_dialog
from config import API_PATH

def api_checker(path):
    try:
        requests.get(API_PATH, timeout=3)
    except Exception as e:
        print(f"EXCEPTION OCCURRED - {e}")
        sys.exit("""API is not running
Check the connection to the internet and the API server.
Chock the endpoint path in the config.py file.""")



if __name__ == "__main__":
    api_checker(API_PATH)


    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    # 2. Apply the custom_widgets_folder stylesheet
    current_style = app.styleSheet()
    try:
        custom_css = (Path(__file__).parent.resolve() / "css" / "app_stylesheet.css").read_text(encoding="utf-8")
        custom_css_gemini = (Path(__file__).parent.resolve() / "css" / "app_stylesheet_gemini.css").read_text(encoding="utf-8")
        app.setStyleSheet(current_style + "\n" + custom_css + custom_css_gemini)
    except FileNotFoundError:
        pass
    # TODO: check for update comment
    check_for_update = check_for_updates()
    if check_for_update:
        confirmation  = confirmation_dialog(None, "Update Available", "A new version of the application is available. Do you want to update now?")
        if confirmation == QMessageBox.Yes:
            try:
                os.startfile("updater.exe")
            except FileNotFoundError:
                QMessageBox.critical(None, "Warning", "Update process aborted. Please reinstall application and try again")


    root = MainFrame()
    root.show()

    app.exec()