from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel, QCheckBox, \
    QComboBox, QStyledItemDelegate, QFrame, QDialogButtonBox
from PySide6.QtGui import QStandardItem, QFontMetrics, QPalette
from PySide6.QtCore import Qt, QEvent

from PySide6.QtGui import QStandardItem, QPalette, QFontMetrics, QStandardItemModel, QBrush, QColor
from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QApplication
from PySide6.QtCore import Qt, QEvent


class CheckableComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        palette = QApplication.palette()
        palette.setBrush(QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        self.setItemDelegate(CheckableComboBox.Delegate())

        self.model().dataChanged.connect(self.updateText)

        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        self.view().viewport().installEventFilter(self)

    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def eventFilter(self, object, event):
        if object == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True

        if object == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                print("item check state after click", item.checkState())
                return True

        return False

    def showPopup(self):
        super().showPopup()
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        self.startTimer(100)
        self.updateText()

    def timerEvent(self, event):
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def currentData(self):
        res = []
        for i in range(self.model().rowCount()):
            print("current", self.model().item(i).checkState())
            if self.model().item(i).checkState() == Qt.Checked:
                print("pass shod")
                res.append(self.model().item(i).data())
        return res


class Replicate:
    def __init__(self, mainPage):
        print("grid", mainPage)
        self.mainPage = mainPage
        print(self.mainPage.mainPage.grid)
        self.dialog = None
        self.layout = None
        self.source_story = None
        self.target_story = None

    # SLOT
    def rep_exec(self):
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Replicate")

        self.layout = QVBoxLayout()

        # Set up combo box 1
        self.label1 = QLabel("Select Source Story:")
        self.source_story = QComboBox()
        self.source_story.addItems([f"Story{i + 1}" for i in range(len(self.mainPage.mainPage.grid))])

        # Set up combo box 2
        self.label2 = QLabel("Select Target Stories:")
        self.target_story = CheckableComboBox()
        self.target_story.addItems([f"Story{i + 1}" for i in range(len(self.mainPage.mainPage.grid))])

        # Set up check boxes
        self.checkbox_post = QCheckBox("Post")
        self.checkbox_beam = QCheckBox("Beam")
        self.checkbox_joist = QCheckBox("Joist")
        self.checkbox_shearWall = QCheckBox("Shear Wall")
        self.checkbox_studWall = QCheckBox("Stud Wall")
        self.checkbox_loadMap = QCheckBox("Load Map")

        # Add labels, combo boxes and check boxes to layout
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.source_story)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.target_story)
        self.layout.addWidget(self.checkbox_post)
        self.layout.addWidget(self.checkbox_beam)
        self.layout.addWidget(self.checkbox_joist)
        self.layout.addWidget(self.checkbox_shearWall)
        self.layout.addWidget(self.checkbox_studWall)
        self.layout.addWidget(self.checkbox_loadMap)

        # Create a buttonbox for ok and cancel
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Connect signals
        self.buttonBox.accepted.connect(self.accept_control)
        self.buttonBox.rejected.connect(self.dialog.reject)

        # Add buttonbox to layout
        self.layout.addWidget(self.buttonBox)

        # Set dialog layout
        self.dialog.setLayout(self.layout)

        self.dialog.exec()

    def accept_control(self):
        sourceTabIndex = int(self.source_story.currentText()[-1]) - 1
        targetTabIndexes = [int(i[-1]) - 1 for i in self.target_story.currentData()]
        copy_list_item = ["post", "beam", "joist", "shearWall", "studWall", "loadMap"]
        item_selected = []
        for i, item in enumerate([self.checkbox_post, self.checkbox_beam, self.checkbox_joist, self.checkbox_shearWall,
                                  self.checkbox_studWall, self.checkbox_loadMap]):
            if item.isChecked():
                item_selected.append(copy_list_item[i])
        copyObject(sourceTabIndex, targetTabIndexes, self.mainPage.mainPage.grid, item_selected)

        self.dialog.accept()


class copyObject:
    def __init__(self, sourceTabIndex, targetTabIndexes, grid, items):
        sourceTab = grid[sourceTabIndex]
        postObjects = list(sourceTab.post_instance.post_prop.values())
        beamObjects = list(sourceTab.beam_instance.beam_rect_prop.values())
        joistObjects = list(sourceTab.joist_instance.rect_prop.values())
        shearWallObjects = list(sourceTab.shearWall_instance.shearWall_rect_prop.values())
        studWallObjects = list(sourceTab.studWall_instance.studWall_rect_prop.values())
        loadMapObjects = list(sourceTab.load_instance.rect_prop.values())
        for i in targetTabIndexes:
            targetTab = grid[i]
            for item in items:
                if item == "post":
                    for postProp in postObjects:
                        targetTab.post_instance.draw_post_mousePress(None, None, postProp)
                elif item == "beam":
                    for beamProp in beamObjects:
                        targetTab.beam_instance.draw_beam_mousePress(None, None, beamProp)
                elif item == "joist":
                    for joistProp in joistObjects:
                        targetTab.joist_instance.draw_joist_mousePress(None, None, joistProp)
                elif item == "shearWall":
                    for shearWallProp in shearWallObjects:
                        targetTab.shearWall_instance.draw_shearWall_mousePress(None, None, shearWallProp)
                elif item == "studWall":
                    for studWallProp in studWallObjects:
                        targetTab.studWall_instance.draw_studWall_mousePress(None, None, studWallProp["coordinate"])
                elif item == "loadMap":
                    for loadProp in loadMapObjects:
                        targetTab.load_instance.draw_load_mousePress(None, None, loadProp)
        # joistProp = list(self.mainPage.mainPage.grid[0].joist_instance.rect_prop.values())
        # self.mainPage.mainPage.grid[1].joist_instance.draw_joist_mousePress(None, None, joistProp[0]["coordinate"])
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.setWindowTitle("Main Window")
#         self.button = QPushButton("Open Dialog")
#         self.button.clicked.connect(self.button_clicked)
#         self.setCentralWidget(self.button)
#
#     def button_clicked(self):
#         dlg = CustomDialog(self)
#         if dlg.exec():
#             print(f"Combo box 1 selection: {dlg.combo_box1.currentText()}")
#             print(f"Multiple combinations: {dlg.combo_box2.currentData()}")
#             print(f"Check box 1 is {'checked' if dlg.checkbox1.isChecked() else 'unchecked'}")
#             print(f"Check box 2 is {'checked' if dlg.checkbox2.isChecked() else 'unchecked'}")
#             print(f"Check box 3 is {'checked' if dlg.checkbox3.isChecked() else 'unchecked'}")
#             print(f"Check box 4 is {'checked' if dlg.checkbox4.isChecked() else 'unchecked'}")
