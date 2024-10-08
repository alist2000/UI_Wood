from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QApplication
from general_properties import h_layout_control
from InformationSaver import InformationSaver


class Widget_form(QWidget):
    def __init__(self, reportInput, parent=None):
        super().__init__(parent)
        screen_geometry = QApplication.primaryScreen().availableGeometry()

        # Calculate the desired width and height
        desired_width = int(screen_geometry.width() * 1 / 2)
        desired_height = int(screen_geometry.height() * 3 / 5)

        # Set the size of the tab widget
        self.setMinimumSize(desired_width, desired_height)

        # VALUES
        self.project_title = None
        self.company = None
        self.designer = None
        self.client = None
        self.comment = None
        self.unit_system = None

        self.reportInput = reportInput

        projectTitle = QLabel("Project Title :")
        projectTitle.setFixedWidth(100)
        self.line_edit_projectTitle = QLineEdit()
        InformationSaver.line_edit_projectTitle = self.line_edit_projectTitle
        h_l1 = h_layout_control(projectTitle, self.line_edit_projectTitle)
        self.line_edit_projectTitle.editingFinished.connect(self.project_title_control)

        company = QLabel("Company :")
        company.setFixedWidth(100)
        self.line_edit_company = QLineEdit()
        InformationSaver.line_edit_company = self.line_edit_company
        h_l2 = h_layout_control(company, self.line_edit_company)
        self.line_edit_company.editingFinished.connect(self.company_control)

        designer = QLabel("Designer :")
        designer.setFixedWidth(100)
        self.line_edit_designer = QLineEdit()
        InformationSaver.line_edit_designer = self.line_edit_designer
        h_l3 = h_layout_control(designer, self.line_edit_designer)
        self.line_edit_designer.editingFinished.connect(self.designer_control)

        client = QLabel("Client :")
        client.setFixedWidth(100)
        self.line_edit_client = QLineEdit()
        InformationSaver.line_edit_client = self.line_edit_client
        h_l4 = h_layout_control(client, self.line_edit_client)
        self.line_edit_client.editingFinished.connect(self.client_control)

        comment = QLabel("Comment :")
        comment.setFixedWidth(100)
        self.line_edit_comment = QLineEdit()
        InformationSaver.line_edit_comment = self.line_edit_comment
        h_l5 = h_layout_control(comment, self.line_edit_comment)
        self.line_edit_comment.editingFinished.connect(self.comment_control)

        unit = QLabel("Unit System :")
        unit.setFixedWidth(100)
        self.unit_combo = QComboBox()
        InformationSaver.unit_combo = self.unit_combo
        self.unit_combo.addItems(["US"])  # "Metric" should be developed!
        h_l6 = h_layout_control(unit, self.unit_combo)
        self.unit_combo.activated.connect(self.unit_control)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_l1)
        v_layout.addLayout(h_l2)
        v_layout.addLayout(h_l3)
        v_layout.addLayout(h_l4)
        v_layout.addLayout(h_l5)
        v_layout.addLayout(h_l6)

        self.setLayout(v_layout)

    # SLOT
    def project_title_control(self):
        self.project_title = self.line_edit_projectTitle.text()
        # REPORT INPUTS
        self.reportInput.Information(
            [self.project_title, self.company, self.designer, self.client, self.comment, self.unit_system])

    # SLOT
    def company_control(self):
        self.company = self.line_edit_company.text()
        # REPORT INPUTS
        self.reportInput.Information(
            [self.project_title, self.company, self.designer, self.client, self.comment, self.unit_system])

    # SLOT
    def designer_control(self):
        self.designer = self.line_edit_designer.text()
        # REPORT INPUTS
        self.reportInput.Information(
            [self.project_title, self.company, self.designer, self.client, self.comment, self.unit_system])

    # SLOT
    def client_control(self):
        self.client = self.line_edit_client.text()
        # REPORT INPUTS
        self.reportInput.Information(
            [self.project_title, self.company, self.designer, self.client, self.comment, self.unit_system])

    # SLOT
    def comment_control(self):
        self.comment = self.line_edit_comment.text()
        # REPORT INPUTS
        self.reportInput.Information(
            [self.project_title, self.company, self.designer, self.client, self.comment, self.unit_system])

    # SLOT
    def unit_control(self, index):
        self.unit_system = self.unit_combo.itemText(index)
        # REPORT INPUTS
        self.reportInput.Information(
            [self.project_title, self.company, self.designer, self.client, self.comment, self.unit_system])
