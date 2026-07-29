from PySide6.QtWidgets import QMessageBox
from pathlib import Path
from fpdf import FPDF
import io


from database.models import ServiceProjects, Projects, ProjectDetails


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
def project_summary_pdf(database,project_id):
    with database.session() as session:
        items = session.query(ProjectDetails).filter(ProjectDetails.project_id == project_id, ProjectDetails.item.isnot(None)).all()
        activities = session.query(ProjectDetails).filter(ProjectDetails.project_id == project_id, ProjectDetails.activity.isnot(None)).all()

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
        session.commit()
"""def prepare_eml_with_attachment(subject, body, file_path):
    # 1. Create the message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg.set_content(body)

    # 2. Attach the file
    with open(file_path, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(
            file_data,
            maintype='application',
            subtype='pdf',
            filename=os.path.basename(file_path)
        )

    # 3. Create a unique temporary file that ends in .eml
    # delete=False is important, so the OS can still see/open it
    # after Python closes the handle
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.eml', delete=False) as f:
        f.write(msg.as_bytes())
        temp_path = f.name

    # 4. Open in the default system mail client
    QDesktopServices.openUrl(QUrl.fromLocalFile(temp_path))"""















