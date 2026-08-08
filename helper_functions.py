from types import SimpleNamespace
from PySide6.QtWidgets import QMessageBox
from pathlib import Path
import sys
from database.models import ServiceProjects, Projects
from API.api import API_CLIENT
import metadata


def clear_layout(layout, grid_layout=False):
    # grid_layout=False will delete all widgets in the layout
    # grid_layout=True will delete all widgets and clear stretch factors if layout is QGridLayout
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
        elif child.layout():
            clear_layout(child.layout())
    if grid_layout:
        # clear stretch factors for rows
        for i in range(layout.rowCount()):
            layout.setRowStretch(i, 0)
            layout.setRowMinimumHeight(i, 0)
        # clear stretch factors for columns
        for j in range(layout.columnCount()):
            layout.setColumnStretch(j, 0)
            layout.setColumnMinimumWidth(j, 0)
def confirmation_dialog(parent, title, message,):
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    return dialog.exec()
def create_pdf_form(database,project_id):
    import io
    import pypdf
    with database.session() as session:
        project = session.query(ServiceProjects).get(project_id)
        empty_pdf_form_path = Path("files/service_form.pdf")
        reader = pypdf.PdfReader(empty_pdf_form_path)
        writer = pypdf.PdfWriter()
        writer.append(reader)
        data = {"number": project.number,
                "owner": project.owner,
                "phone_number": project.phone_number}
        writer.update_page_form_field_values(writer.pages[0],data)
        # Saving the Pdf to a BytesIO object and then to a database field
        bytes_stream = io.BytesIO() # create a BytesIO object
        writer.write(bytes_stream) # write pdf content to the BytesIO object
        project.pdf_form = bytes_stream.getvalue() # get the content of the BytesIO object
        session.commit()
def project_summary_pdf(project_id):
    # Todo : project_summary

    """items = API_CLIENT.get(f"/projects/{project_id}/items/").json()
    items = [SimpleNamespace(**item) for item in items]
    activities = API_CLIENT.get(f"/projects/{project_id}/activities/").json()
    activities = [SimpleNamespace(**activity) for activity in activities]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font(family="Arial", style='b', size=12)
    pdf.cell(text="ITEMS")
    if items:
        for item in items:
            pdf.cell(text=item.item, ln=1)
    else:
        pdf.cell(text="No Items")
    pdf.cell(text="", w=1,h=2)
    if activities:
        for activity in activities:
            pdf.cell(text=activity.activity, ln=1)
    else:
        pdf.cell(text="No Activities")

    # Create temporary file
    temp_file = io.BytesIO()
    pdf.output(temp_file)


    with database.session() as session:
        project = session.get(Projects, project_id)
        raw_bytes = temp_file.getvalue()
        project.summary_pdf = raw_bytes
        session.commit()"""
def check_for_updates():
    # Function check if there is an update available
    app_version_id = metadata.VERSION_ID
    app_metadata = API_CLIENT.get("/app_metadata/latest_version")
    if app_metadata.status_code == 200:
        latest_version_id = app_metadata.json()["id"]
        latest_version_number = app_metadata.json()["version"]
    else:
        return False
    # Compare actual version id with latest version id from the API

    if app_version_id < latest_version_id: # -> there is more actual version
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Update Available")
        msg_box.setText(f"There is a new version of the app available. Do You want to update to version?: {latest_version_number}.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg_box.exec()
        if result == QMessageBox.Yes:
            return True
        return False
    return False
def get_app_version(flag=None):
    # Function returns the app version
    if flag == "id":
        return metadata.VERSION_ID
    elif flag == "number":
        return metadata.VERSION
    else:
        return f"{metadata.VERSION} (ID: {metadata.VERSION_ID})"


def update_app():
    # TODO: Write in Rust
    print("Updating app...")


















