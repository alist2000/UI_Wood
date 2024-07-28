from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMessageBox
from UI_Wood.stableVersion5.styles import TabWidgetStyle
from report.report import Inputs
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDoubleSpinBox, QLabel, QPushButton, \
    QTextEdit, QAbstractItemView, QTableWidget, \
    QRadioButton, QSpacerItem, QGraphicsView, QGraphicsScene
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QApplication
from InformationSaver import InformationSaver
from UI_Wood.stableVersion5.grid_define import GridCoordinateDefine, GridPreview, \
    StoryCoordinateDefine



class EditProperties(QWidget):
    def __init__(self, mainPage, parent=None):
        super().__init__(parent)
        self.mainPage = mainPage

        # Inputs for Report
        reportInputs = Inputs()

        self.setWindowTitle("WOOD DESIGN APPLICATION")

        tab_widget = QTabWidget(self)
        self.setStyleSheet(TabWidgetStyle)

        # Information - Tab 1
        self.widget_form = Widget_form(reportInputs)

        # Buttons - Tab 2
        self.widget_buttons = Widget_button(reportInputs, mainPage)

        # Add tabs to widget
        tab_widget.addTab(self.widget_form, "General Information")
        tab_widget.addTab(self.widget_buttons, "General Properties")

        layout = QVBoxLayout()
        layout.addWidget(tab_widget)

        self.setLayout(layout)

    def showEvent(self, event):
        # Get the screen size
        screen_geometry = QApplication.primaryScreen().availableGeometry()

        # Calculate the center of the screen
        center = screen_geometry.center()

        # Calculate the position of the tab widget to place it in the center of the screen
        rect = self.frameGeometry()
        rect.moveCenter(center)

        # Move the tab widget to the calculated position
        self.move(rect.topLeft())

        midLineDict = {}
        for currentTab in range(self.mainPage.mainPage.level_number - 1, -1, -1):
            midLineData, lineLabels, boundaryLineLabels = self.mainPage.mainPage.grid[currentTab].run_control()
            if currentTab == self.mainPage.mainPage.level_number - 1:
                storyName = "Roof"
            else:
                storyName = str(currentTab + 1)

            midLineDict[storyName] = midLineData

        self.mainPage.savePage.save_data()

        # generalProp = ControlGeneralProp(self.general_properties)
        # Update widgets with new data
        self.update_widgets()

        super().showEvent(event)

    def update_widgets(self):
        # Fetch the latest data
        form_data = self.get_form_data()
        button_data = self.get_button_data()

        # Update the widgets
        self.widget_form.update_data(form_data)
        self.widget_buttons.update_data(button_data)

    def get_form_data(self):
        # Fetch the latest form data from your data source
        # This is just an example, replace with your actual data fetching logic
        return self.mainPage.mainPage.information_properties

    def get_button_data(self):
        # Fetch the latest button data from your data source
        # This is just an example, replace with your actual data fetching logic
        return self.mainPage.mainPage.inputs


def h_layout_control(*args):
    h_layout = QHBoxLayout()
    for item in args:
        h_layout.addWidget(item)
    return h_layout


class Widget_button(QWidget):
    def __init__(self, reportInputs, mainPage, parent=None):
        super().__init__(parent)
        # final values
        self.level_final = None
        self.h_grid_number_final = None
        self.v_grid_number_final = None
        self.height_story_final = None
        self.h_spacing_final = None
        self.v_spacing_final = None
        self.tabWidget = None
        self.mainPage = mainPage
        self.x_grid, self.y_grid, self.grid_base = None, None, None
        # self.loadInstance = Load(self)

        # REPORT INPUTS
        self.reportInputs = reportInputs

        # for new tab
        self.new_window = None

        self.setMinimumSize(600, 500)

        storyHeightLayout = QHBoxLayout()
        self.storyInstance = StoryCoordinateDefine()
        spacer = QSpacerItem(380, 20)
        storyHeightLayout.addWidget(self.storyInstance)
        # storyHeightLayout.addItem(spacer)

        self.gridInstance = GridCoordinateDefine()
        self.previewGrid = GridPreview(self.gridInstance)
        self.previewButton = QPushButton("PREVIEW")
        self.previewButton.clicked.connect(self.previewGrid.preview)
        previewLayout = QVBoxLayout()
        previewLayout.addWidget(self.previewGrid)
        previewLayout.addWidget(self.previewButton)
        storyHeightLayout.addLayout(previewLayout)

        # RUN Button
        self.height_story = []
        self.h_spacing_list = []
        self.v_spacing_list = []
        run = QPushButton("APPLY")
        # load = QPushButton("LOAD")
        run.clicked.connect(self.run_control)
        # load.clicked.connect(self.loadInstance.load_control)

        v_layout = QVBoxLayout()
        v_layout.addLayout(storyHeightLayout)
        v_layout.addWidget(self.gridInstance)
        v_layout.addWidget(run)
        # v_layout.addWidget(load)
        self.setLayout(v_layout)

    # SLOT FUNCTION
    def run_control(self):
        from load import set_toolBar, drawing
        response = self.show_warning_message()
        if response == QMessageBox.Yes:
            self.previewGrid.preview()
            self.x_grid, self.y_grid, self.grid_base = self.gridInstance.output()
            self.level_final, self.height_story_final = self.storyInstance.output()

            height_story = self.height_story
            height_story.clear()
            print("run")

            # REPORT INPUTS
            self.reportInputs.General_prop(self.result())
            self.mainPage.savePage.save_data()
            self.create_main_tab()
            self.mainPage.savePage.data["general_properties"] = self.result()
            set_toolBar(self.mainPage.savePage.data, self.tabWidget.toolBar)
            drawing(self.mainPage.savePage.data, self.tabWidget.grid)
            # Close the current window and open a new one with updated data
            # self.parent().close()
            # Add code here to open a new window with the updated data
        else:
            print("Operation cancelled by user")

    def create_main_tab(self):
        from tab_widget_2 import secondTabWidget
        from load import UpdateGridData
        # Set Information Properties
        self.line_edit_projectTitle = QLineEdit(self.mainPage.savePage.data["general_information"]["project_name"])
        InformationSaver.line_edit_projectTitle = self.line_edit_projectTitle
        self.line_edit_company = QLineEdit(self.mainPage.savePage.data["general_information"]["company"])
        InformationSaver.line_edit_company = self.line_edit_company
        self.line_edit_designer = QLineEdit(self.mainPage.savePage.data["general_information"]["designer"])
        InformationSaver.line_edit_designer = self.line_edit_designer
        self.line_edit_client = QLineEdit(self.mainPage.savePage.data["general_information"]["client"])
        InformationSaver.line_edit_client = self.line_edit_client
        self.line_edit_comment = QLineEdit(self.mainPage.savePage.data["general_information"]["comment"])
        InformationSaver.line_edit_comment = self.line_edit_comment
        self.unit_combo = QComboBox()
        self.unit_combo.addItem(self.mainPage.savePage.data["general_information"]["unit_system"])
        self.unit_combo.setCurrentText(self.mainPage.savePage.data["general_information"]["unit_system"])
        InformationSaver.unit_combo = self.unit_combo

        # set second tab features.
        general_properties = self.mainPage.savePage.data["general_properties"]
        UpdateGridData(general_properties)
        self.tabWidget = secondTabWidget(general_properties)

    def result(self):
        Result = {"level_number": self.level_final, "height_story": self.height_story_final,
                  "x_grid": self.x_grid,
                  "y_grid": self.y_grid,
                  "grid_base": self.grid_base}
        return Result

    def show_warning_message(self):
        warning_box = QMessageBox()
        warning_box.setIcon(QMessageBox.Warning)
        warning_box.setWindowTitle("Warning")
        warning_box.setText("Important Notice")
        warning_box.setInformativeText(
            "By proceeding, This window will close, and a new one will open with the updated data. "
            "Are you sure you want to continue?")
        warning_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        warning_box.setDefaultButton(QMessageBox.No)
        return warning_box.exec_()

    def update_data(self, data):
        self.storyInstance.update_data(data.get("level_number", 1), data.get("height_story", []),
                                       data.get("grid_base", "coordinate"))
        self.gridInstance.update_data(data.get("x_grid", []), data.get("y_grid", []),
                                      data.get("grid_base", "coordinate"))
        self.previewGrid.preview()

        # Update the reportInputs
        self.reportInputs.General_prop(data)


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
        self.unit_combo.addItems(["US", "Metric"])
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

    def update_data(self, data):
        self.line_edit_projectTitle.setText(data.get("project_name", ""))
        self.line_edit_company.setText(data.get("company", ""))
        self.line_edit_designer.setText(data.get("designer", ""))
        self.line_edit_client.setText(data.get("client", ""))
        self.line_edit_comment.setText(data.get("comment", ""))
        index = self.unit_combo.findText(data.get("unit_system", ""))
        if index >= 0:
            self.unit_combo.setCurrentIndex(index)

        # Update the reportInput
        self.reportInput.Information([
            data.get("project_name", ""),
            data.get("company", ""),
            data.get("designer", ""),
            data.get("client", ""),
            data.get("comment", ""),
            data.get("unit_system", "")
        ])

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
