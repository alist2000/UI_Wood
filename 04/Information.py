from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox
from general_properties import h_layout_control


class Widget_form(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(600, 500)

        projectTitle = QLabel("Project Title :")
        projectTitle.setFixedWidth(100)
        line_edit_projectTitle = QLineEdit()
        h_l1 = h_layout_control(projectTitle, line_edit_projectTitle)

        company = QLabel("Company :")
        company.setFixedWidth(100)
        line_edit_company = QLineEdit()
        h_l2 = h_layout_control(company, line_edit_company)

        designer = QLabel("Designer :")
        designer.setFixedWidth(100)
        line_edit_designer = QLineEdit()
        h_l3 = h_layout_control(designer, line_edit_designer)

        client = QLabel("Client :")
        client.setFixedWidth(100)
        line_edit_client = QLineEdit()
        h_l4 = h_layout_control(client, line_edit_client)

        comment = QLabel("Comment :")
        comment.setFixedWidth(100)
        line_edit_comment = QLineEdit()
        h_l5 = h_layout_control(comment, line_edit_comment)

        unit = QLabel("Unit System :")
        unit.setFixedWidth(100)
        unit_combo = QComboBox()
        unit_combo.addItems(["US", "Metric"])
        h_l6 = h_layout_control(unit, unit_combo)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_l1)
        v_layout.addLayout(h_l2)
        v_layout.addLayout(h_l3)
        v_layout.addLayout(h_l4)
        v_layout.addLayout(h_l5)
        v_layout.addLayout(h_l6)

        self.setLayout(v_layout)
