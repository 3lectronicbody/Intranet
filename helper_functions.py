from PySide6.QtWidgets import QMessageBox
from pathlib import Path
import pypdf

from database.models import ServiceProjects


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
        empty_pdf_form_path = Path("files/service form.pdf")
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















