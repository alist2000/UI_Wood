from UI_Wood.stableVersion5.output.beam_output import beam_output
from UI_Wood.stableVersion5.Sync.Transfer import Transfer, DeleteTransferred
from UI_Wood.stableVersion5.Sync.mainSync import ControlGeneralProp
from UI_Wood.stableVersion5.styles import TabWidgetStyle

from PySide6.QtWidgets import (QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QTableWidget, QTableWidgetItem,
                               QHeaderView, QStyledItemDelegate, QApplication, QDialog, QGroupBox)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont, QPalette


class BeamCheck:
    def __init__(self, tab, general_properties):
        self.tab = tab
        self.general_properties = general_properties
        self.beam_check_page = None
        generalProp = ControlGeneralProp(self.general_properties)
        height_from_top = list(reversed(generalProp.height))

        tabReversed = self.reverse_dict(self.tab)  # top to bottom
        TransferInstance = Transfer()

        beams = []
        beam_outputs = []
        j = 0
        shearWallTop = None
        studWallTop = None
        heightTop = None
        storySWTop = None
        postTop = None
        shearWallTop = None
        for story, Tab in tabReversed.items():
            beam = Tab["beam"]
            beams.append(beam)
            post = Tab["post"]
            shearWall = Tab["shearWall"]
            studWall = Tab["studWall"]

            if j == 0:
                storySW = "Roof"
            else:
                storySW = story + 1

            # CONTROL STACK
            TransferInstance.StackControl(shearWallTop, shearWall, storySW, "shearWall")
            TransferInstance.StackControl(studWallTop, studWall, storySW, "studWall")
            TransferInstance.StackControl(postTop, post, storySW, "post")
            print("This list should be transferred: ", TransferInstance.transferListShearWall)

            # Delete Transferred items. This list is for check model
            TransferInstance.DeleteTransferredItems(beam)

            # Transfer Gravity and Earthquake loads from Transferred shearWalls to beams.
            try:
                TransferInstance.TransferOtherLoads(shearWallTop, beam, heightTop, "shearWall", storySWTop)
            except:
                pass

            # Transfer Gravity loads from Transferred studWalls to beams.
            TransferInstance.TransferOtherLoads(studWallTop, beam, heightTop, "studWall")

            # Transfer Gravity loads from Transferred posts to beam.
            TransferInstance.TransferPointLoads(postTop, beam)

            beamOutput = beam_output(beam)

            beam_outputs.append(beamOutput.beamProperties)

            postTop = post
            shearWallTop = shearWall
            studWallTop = studWall
            heightTop = height_from_top[j]
            storySWTop = storySW

            j += 1

        print(beam_outputs)
        self.beam_check_page = BeamPropertiesWidget(beam_outputs)
        self.beam_check_page.show()
        DeleteTransferred(beams)

    @staticmethod
    def reverse_dict(Dict):
        key = list(Dict.keys())
        value = list(Dict.values())
        key.reverse()
        value.reverse()
        newDict = {}
        for k, v in zip(key, value):
            newDict[k] = v

        return newDict


class ColorDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if index.row() % 2 == 0:
            option.backgroundBrush = QColor(240, 240, 240)
        else:
            option.backgroundBrush = QColor(255, 255, 255)


class BeamPropertiesWidget(QTabWidget):
    show_beam_signal = Signal(str)

    def __init__(self, beam_properties):
        super().__init__()
        self.beam_properties = beam_properties
        self.setup_ui()
        self.setStyleSheet(TabWidgetStyle)
        self.setWindowTitle("Beam Check")

        # self.setStyleSheet("""
        #     QTabWidget::pane {
        #         border: 1px solid #cccccc;
        #         background: white;
        #         border-radius: 5px;
        #     }
        #     QTabWidget::tab-bar {
        #         left: 5px;
        #     }
        #     QTabBar::tab {
        #         background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        #                                     stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
        #                                     stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
        #         border: 1px solid #C4C4C3;
        #         border-bottom-color: #C2C7CB;
        #         border-top-left-radius: 4px;
        #         border-top-right-radius: 4px;
        #         min-width: 8ex;
        #         padding: 2px;
        #     }
        #     QTabBar::tab:selected, QTabBar::tab:hover {
        #         background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        #                                     stop: 0 #fafafa, stop: 0.4 #f4f4f4,
        #                                     stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
        #     }
        #     QTabBar::tab:selected {
        #         border-color: #9B9B9B;
        #         border-bottom-color: #C2C7CB;
        #     }
        # """)

    def setup_ui(self):
        for story_index, story in enumerate(reversed(self.beam_properties)):
            story_name = f"Story {story_index + 1}"
            story_widget = QWidget()
            story_layout = QVBoxLayout(story_widget)

            table = self.create_story_table(story)
            story_layout.addWidget(table)

            self.addTab(story_widget, story_name)

        # Set the size of the widget
        self.resize(800, 600)
        # Center the widget on the screen
        self.center_on_screen()

    def create_story_table(self, story):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setRowCount(len(story))
        table.setHorizontalHeaderLabels(["Label", "Length (ft)", "Number of Supports", "Detail", "Show Beam"])

        # Set the delegate for alternating row colors
        delegate = ColorDelegate(table)
        table.setItemDelegate(delegate)

        # Remove grid lines
        table.setShowGrid(False)

        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #dcdcdc;
                font-weight: bold;
            }
        """)

        for row, beam in enumerate(story):
            table.setItem(row, 0, QTableWidgetItem(beam['label']))
            table.setItem(row, 1, QTableWidgetItem(f"{beam['length']:.2f}"))
            table.setItem(row, 2, QTableWidgetItem(str(len(beam['support']))))

            detail_button = QPushButton("Detail")
            detail_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    padding: 5px 10px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 12px;
                    margin: 4px 2px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            detail_button.clicked.connect(lambda _, b=beam: self.show_detail(b))
            table.setCellWidget(row, 3, detail_button)

            show_beam_button = QPushButton("Show Beam")
            show_beam_button.setEnabled(False)
            show_beam_button.setStyleSheet("""
                QPushButton {
                    background-color: #008CBA;
                    border: none;
                    color: white;
                    padding: 5px 10px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 12px;
                    margin: 4px 2px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #007B9A;
                }
            """)
            show_beam_button.clicked.connect(lambda _, label=beam['label']: self.show_beam_signal.emit(label))
            table.setCellWidget(row, 4, show_beam_button)

        return table

    def show_detail(self, beam):
        detail_dialog = BeamDetailDialog(beam, self)
        detail_dialog.exec()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)


class BeamDetailDialog(QDialog):
    def __init__(self, beam, parent=None):
        super().__init__(parent)
        self.beam = beam
        self.setWindowTitle(f"Beam {beam['label']} Details")
        self.setMinimumSize(500, 600)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Geometry Properties
        geometry_group = self.create_group_box("Geometry Properties")
        geometry_layout = QVBoxLayout()
        geometry_layout.addWidget(self.create_info_widget("Coordinate", f"{self.beam['coordinate']}"))
        geometry_layout.addWidget(self.create_info_widget("Length", f"{self.beam['length']:.2f}"))
        geometry_layout.addWidget(self.create_info_widget("Direction", self.beam['direction']))
        geometry_layout.addWidget(self.create_info_widget("Supports", self.format_supports()))
        geometry_group.setLayout(geometry_layout)
        scroll_layout.addWidget(geometry_group)

        # Load Properties
        load_group = self.create_group_box("Load Properties")
        load_layout = QVBoxLayout()
        load_layout.addWidget(QLabel("Point Loads:"))
        load_layout.addWidget(self.create_point_loads_table())
        load_layout.addWidget(QLabel("Distributed Loads:"))
        load_layout.addWidget(self.create_distributed_loads_table())
        load_group.setLayout(load_layout)
        scroll_layout.addWidget(load_group)

        # Transferred Items
        if self.beam.get('transfer_item'):
            transfer_group = self.create_group_box("Transferred Items")
            transfer_layout = QVBoxLayout()
            for item in self.beam['transfer_item']:
                transfer_layout.addWidget(self.create_info_widget(item['item'], item['label']))
            transfer_group.setLayout(transfer_layout)
            scroll_layout.addWidget(transfer_group)

        # Additional Properties
        additional_group = self.create_group_box("Additional Properties")
        additional_layout = QVBoxLayout()
        additional_layout.addWidget(self.create_info_widget("Material", self.beam['material']))
        additional_layout.addWidget(self.create_info_widget("Floor", "Yes" if self.beam['floor'] else "No"))
        additional_group.setLayout(additional_layout)
        scroll_layout.addWidget(additional_group)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

    def create_group_box(self, title):
        group_box = QGroupBox(title)
        font = QFont()
        font.setBold(True)
        group_box.setFont(font)
        return group_box

    def create_info_widget(self, label, value):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        label_widget = QLabel(f"{label}:")
        label_widget.setMinimumWidth(120)
        font = label_widget.font()
        font.setBold(True)
        label_widget.setFont(font)
        value_widget = QLabel(str(value))
        value_widget.setWordWrap(True)
        layout.addWidget(label_widget)
        layout.addWidget(value_widget, 1)
        return widget

    def format_supports(self):
        return ", ".join([f"({support[0]:.2f}, {support[1]})" for support in self.beam['support']])

    def create_point_loads_table(self):
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Start", "Type", "Magnitude"])

        point_loads = self.beam['load']['point']
        point_load_numbers = 0
        for point in point_loads:
            for i in point["load"]:
                point_load_numbers += 1
        table.setRowCount(point_load_numbers)
        row_main = 0
        for row1, load in enumerate(point_loads):
            table.setItem(row_main, 0, QTableWidgetItem(f"{load['start']:.2f}"))
            for row, load_info in enumerate(load['load']):
                table.setItem(row_main, 1, QTableWidgetItem(load_info['type']))
                table.setItem(row_main, 2, QTableWidgetItem(f"{load_info['magnitude']}"))
                row_main += 1

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)

        if not point_loads:
            table.setRowCount(1)
            table.setSpan(0, 0, 1, 3)
            table.setItem(0, 0, QTableWidgetItem("No point loads"))

        return table

    def create_distributed_loads_table(self):
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Start", "End", "Type", "Magnitude"])

        distributed_loads = self.beam['load']['distributed']
        total_rows = sum(len(load['load']) for load in distributed_loads)
        table.setRowCount(total_rows)

        row = 0
        for dist_load in distributed_loads:
            start = dist_load['start']
            end = dist_load['end']
            for load_info in dist_load['load']:
                table.setItem(row, 0, QTableWidgetItem(f"{start:.2f}"))
                table.setItem(row, 1, QTableWidgetItem(f"{end:.2f}"))
                table.setItem(row, 2, QTableWidgetItem(load_info['type']))
                table.setItem(row, 3, QTableWidgetItem(f"{load_info['magnitude']}"))
                row += 1

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)

        if not distributed_loads:
            table.setRowCount(1)
            table.setSpan(0, 0, 1, 4)
            table.setItem(0, 0, QTableWidgetItem("No distributed loads"))

        return table
# Update the show_detail method in BeamPropertiesWidget


# Don't forget to update the import statement at the top of your main file:
# from beam_detail_dialog import BeamDetailDialog
