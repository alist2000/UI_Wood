from PySide6.QtCore import Qt, QRect, QPoint, QSize, QEvent
from PySide6.QtGui import QFont, QColor, QPen, QBrush, QLinearGradient, QPainter, QUndoStack

from PySide6.QtWidgets import QTabWidget, QDialog, QDialogButtonBox, \
    QLabel, QWidget, QVBoxLayout, QPushButton, QGraphicsProxyWidget, QGraphicsRectItem, QHBoxLayout, \
    QGraphicsView, QGraphicsScene, QGraphicsSceneMouseEvent, QListWidget, QListWidgetItem, QDoubleSpinBox, QCheckBox

from UI_Wood.stableVersion5.post_new import magnification_factor
from UI_Wood.stableVersion5.layout.LineDraw import BeamLabel
from UI_Wood.stableVersion5.grid import SelectCommand, DeselectCommand
from UI_Wood.stableVersion5.navigation_graphics_view import NavigationGraphicsView


class ShearWallsView(NavigationGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = self
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.undoStack = QUndoStack()

    # def resizeEvent(self, event):
    #     # Call the base class implementation to handle the resize event
    #     super(ShearWallsView, self).resizeEvent(event)
    #
    #     # Fit the view to the scene and center the contents
    #     self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
    #     self.centerOn(self.scene.itemsBoundingRect().center())

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton or (
                event.button() == Qt.LeftButton and event.modifiers() & Qt.AltModifier):
            self.pan_active = True
            self.last_pan_point = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        if event.button() == Qt.LeftButton:
            self.view.setRenderHint(QPainter.Antialiasing)
            self.view.setRenderHint(QPainter.SmoothPixmapTransform)
            self.view.setDragMode(QGraphicsView.ScrollHandDrag)
            self.view.viewport().setCursor(Qt.OpenHandCursor)

        item = self.view.itemAt(event.pos())
        print(item)
        if item:
            isSelected = item.isSelected()
            command = DeselectCommand(item) if isSelected else SelectCommand(item)
            self.undoStack.push(command)

            # Create a QGraphicsSceneMouseEvent and set its properties
            sceneEvent = QGraphicsSceneMouseEvent(QEvent.GraphicsSceneMousePress)
            sceneEvent.setScenePos(self.view.mapToScene(event.position().toPoint()))
            sceneEvent.setLastScenePos(self.view.mapToScene(event.position().toPoint()))
            sceneEvent.setScreenPos(event.globalPosition().toPoint())
            sceneEvent.setLastScreenPos(event.globalPosition().toPoint())

            sceneEvent.setButtons(event.buttons())
            sceneEvent.setButton(event.button())
            sceneEvent.setModifiers(event.modifiers())

            item.mousePressEvent(sceneEvent)

            if sceneEvent.isAccepted():
                event.accept()
                return

        super().mousePressEvent(event)


class DrawShearWall(QDialog):
    def __init__(self, GridClass, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)

        self.setWindowTitle("Continue or Break?")
        self.shearWalls = []
        self.selectedWalls = []
        self.labels = []
        self.percents = []
        self.pe = []
        self.Story = None
        self.mainLayout = QVBoxLayout()
        self.view = ShearWallsView()
        self.scene = self.view.scene
        self.view.setRenderHint(QPainter.Antialiasing)  # Corrected attribute
        self.view.setInteractive(True)
        GridClass.Draw(self.scene)
        self.current_rect = None
        self.start_pos = None
        self.other_button = None
        self.shearWall_width = magnification_factor  # Set shearWall width, magnification = 1 ft or 1 m
        # self.post_dimension = min(min(x), min(y)) / 8  # Set post dimension
        self.post_dimension = magnification_factor / 4  # Set post dimension
        self.dimension = None

    def story(self, story):
        mainText = QGraphicsProxyWidget()
        if story == "999999":
            story = "Roof"
        self.Story = story

        dcr = QLabel(f"Story {story}")
        font = QFont()
        font.setPointSize(30)
        dcr.setFont(font)
        dcr.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : black; }")
        mainText.setWidget(dcr)
        mainText.setPos(-150, -150)
        self.scene.addItem(mainText)

    # coordinate = properties["coordinate"]
    # x1, y1 = coordinate[0]
    # x2, y2 = coordinate[1]
    # self.finalize_rectangle_copy((x1, y1), (x2, y2), properties)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def finalize_rectangle_copy(self, start, end, prop, label=None, fromAbove=False):
        x1, y1 = start
        x2, y2 = end
        length = (((x2 - x1) ** 2) + (
                (y2 - y1) ** 2)) ** 0.5
        y1_main = min(y1, y2)
        x1_main = min(x1, x2)
        self.current_rect = Rectangle(x1,
                                      y1)
        self.scene.addItem(self.current_rect)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        if width > height:
            direction = "E-W"
        else:
            direction = "N-S"

        if direction == "E-W":
            self.current_rect.setRect(min(x1, x2),
                                      y1 - self.shearWall_width / 2, abs(width), self.shearWall_width)
        else:
            self.current_rect.setRect(x1 - self.shearWall_width / 2,
                                      min(y1, y2), self.shearWall_width,
                                      abs(height))
        self.shearWalls.append({self.current_rect: prop})

        center_left = QPoint(self.current_rect.boundingRect().left(),
                             self.current_rect.boundingRect().top() + self.current_rect.boundingRect().height() // 2)
        center_right = QPoint(self.current_rect.boundingRect().right(),
                              self.current_rect.boundingRect().top() + self.current_rect.boundingRect().height() // 2)
        center_top = QPoint(self.current_rect.boundingRect().left() + self.current_rect.boundingRect().width() // 2,
                            self.current_rect.boundingRect().top())
        center_bottom = QPoint(self.current_rect.boundingRect().left() + self.current_rect.boundingRect().width() // 2,
                               self.current_rect.boundingRect().bottom())

        # Calculate the positions and sizes for the start and end rectangles
        if direction == "E-W":
            start_rect_pos = QPoint(center_left.x(), center_left.y() - self.current_rect.boundingRect().height() // 2)
            end_rect_pos = QPoint(center_right.x() - (magnification_factor / 2),
                                  center_right.y() - self.current_rect.boundingRect().height() // 2)
            rect_size = QSize((magnification_factor / 2), self.current_rect.boundingRect().height())

        else:
            start_rect_pos = QPoint(center_top.x() - self.current_rect.boundingRect().width() // 2, center_top.y())
            end_rect_pos = QPoint(center_bottom.x() - self.current_rect.boundingRect().width() // 2,
                                  center_bottom.y() - (magnification_factor / 2))
            rect_size = QSize(self.current_rect.boundingRect().width(), (magnification_factor / 2))

        # Create the start and end rectangles
        start_rect = QRect(start_rect_pos, rect_size)
        end_rect = QRect(end_rect_pos, rect_size)
        start_rect_item = QGraphicsRectItem(start_rect)
        end_rect_item = QGraphicsRectItem(end_rect)
        if fromAbove:
            start_rect_item.setPen(QPen(QColor.fromRgb(255, 255, 255, 100), 2, Qt.DashLine))
            end_rect_item.setPen(QPen(QColor.fromRgb(255, 255, 255, 100), 2, Qt.DashLine))
        self.scene.addItem(start_rect_item)
        self.scene.addItem(end_rect_item)
        if not label:
            dcr_shear = prop["dcr_shear"]
            dcr_tension = prop["dcr_tension"]
            dcr_compression = prop["dcr_compression"]
            dcr_deflection = prop["dcr_deflection"]
            dcr = [dcr_shear, dcr_tension, dcr_compression, dcr_deflection]
            color = "green"
            for i in dcr:
                if i > 1:
                    color = "red"
                    break
            if color == "red":
                self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
                self.current_rect.setBrush(QBrush(QColor.fromRgb(245, 80, 80, 100), Qt.SolidPattern))
                self.CheckValuesNew(dcr_shear, dcr_tension, dcr_compression, dcr_deflection, x1_main, y1_main,
                                    direction)

            else:
                self.current_rect.setPen(QPen(QColor.fromRgb(150, 194, 145, 100), 2))
                self.current_rect.setBrush(QBrush(QColor.fromRgb(150, 194, 145, 100), Qt.SolidPattern))
            self.TextValue(f"{prop['type']}", x1_main, y1_main, direction)

            # self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
            # self.current_rect.setBrush(QBrush(QColor.fromRgb(255, 133, 81, 100), Qt.SolidPattern))

            BeamLabel(x1 + length / 2, y1, self.scene, "SW" + prop["label"], direction, (x1, y1))
        else:
            if fromAbove:
                self.current_rect.setPen(QPen(QColor.fromRgb(0, 0, 0, 200), 2, Qt.DashLine))

            else:
                self.current_rect.setPen(QPen(QColor.fromRgb(245, 80, 80, 100), 2))
                self.current_rect.setBrush(QBrush(QColor.fromRgb(255, 133, 81, 100), Qt.SolidPattern))
                BeamLabel(x1 + length / 2, y1, self.scene, label, direction, (x1, y1))

    def CheckValuesNew(self, dcr_shear, dcr_tension, dcr_compression, dcr_deflection, x, y, direction):
        mainText1 = QGraphicsProxyWidget()
        dcr1 = QLabel(f"DCR <sub>shear</sub>: {dcr_shear}, ")
        dcr2 = QLabel(f"DCR <sub>tension</sub>: {dcr_tension}, ")
        dcr3 = QLabel(f"DCR <sub>comp</sub>: {dcr_compression}")
        dcr4 = QLabel(f"DCR <sub>deflection</sub>: {dcr_deflection}")
        font = QFont()
        font.setPointSize(7)
        dcr1.setFont(font)
        dcr2.setFont(font)
        dcr3.setFont(font)
        dcr4.setFont(font)
        layout = QHBoxLayout()
        layout.setSpacing(7)  # Set the space between widgets to 20 pixels
        layout.addWidget(dcr1)
        layout.addWidget(dcr2)
        layout.addWidget(dcr3)
        layout.addWidget(dcr4)
        widget = QWidget()
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: transparent;")
        mainText1.setWidget(widget)
        # text = QGraphicsTextItem("Hello, PySide6!")

        self.setColor(dcr_shear, dcr1)
        self.setColor(dcr_tension, dcr2)
        self.setColor(dcr_compression, dcr3)
        self.setColor(dcr_deflection, dcr4)
        if direction == "N-S":
            mainText1.setRotation(90)
            mainText1.setPos(x - 0.4 * self.shearWall_width, y)
        else:
            mainText1.setPos(x, y + 0.4 * self.shearWall_width)

        # LabelText = QLabel(label)
        self.scene.addItem(mainText1)

    @staticmethod
    def setColor(item, label):
        if item > 1:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : red; }")

        else:
            label.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color : green; }")

    def TextValue(self, text, x, y, direction, color="black", size=10):
        mainText1 = QGraphicsProxyWidget()
        dcr1 = QLabel(text)
        font = QFont()
        font.setPointSize(size)
        dcr1.setFont(font)
        mainText1.setWidget(dcr1)
        # text = QGraphicsTextItem("Hello, PySide6!")

        dcr1.setStyleSheet("QLabel { background-color :rgba(255, 255, 255, 0); color :" + f"{color}" + " ;}")
        if direction == "N-S":
            mainText1.setRotation(90)
            mainText1.setPos(x + 1.1 * self.shearWall_width, y)
        else:
            mainText1.setPos(x, y - 1.1 * self.shearWall_width)

        # LabelText = QLabel(label)
        self.scene.addItem(mainText1)

    def Show(self):
        # Add the view to the layout
        yes_button = QPushButton("Continue")

        no_button = QPushButton("Break")
        yes_button.clicked.connect(self.accept)  # Connect "Yes" button to accept()

        no_button.clicked.connect(self.reject)  # Connect "No" button to reject()
        hLayout = QHBoxLayout()
        hLayout.addWidget(no_button)
        hLayout.addWidget(yes_button)
        self.view.setScene(self.scene)
        self.mainLayout.addWidget(self.view)
        self.mainLayout.addLayout(hLayout)
        self.setLayout(self.mainLayout)
        # self.show()

        # self.setScene(self.scene)
        # self.show()

    def ShowTransfer(self, selectedWalls):
        # Fit the view to the scene and center the contents
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.view.centerOn(self.scene.itemsBoundingRect().center())
        # Add the view to the layout
        yes_button = QPushButton("Next")

        no_button = QPushButton("Cancel")
        yes_button.clicked.connect(self.next)  # Connect "Yes" button to accept()
        # I should open second tab and show selected transferred data

        no_button.clicked.connect(self.reject)  # Connect "No" button to reject()
        hLayout = QHBoxLayout()
        hLayout.addWidget(no_button)
        hLayout.addWidget(yes_button)
        self.view.setScene(self.scene)
        self.mainLayout.addWidget(self.view)
        self.mainLayout.addLayout(hLayout)
        if selectedWalls:
            list_widget = QListWidget(self)
            widget = QWidget()
            titleLayout = QHBoxLayout(widget)
            # Get the last widget in the layout and delete it
            self.delete_widget()
            self.delete_widget()
            # Add labels
            label = QLabel("Label")
            story = QLabel("Percentage")
            pe_title = QLabel("Transfer PE?")
            titles = [label, story, pe_title]
            for i in titles:
                i.setStyleSheet("""
                            font-family: 'Arial';
                            font-size:  14pt;
                            font-weight: bold;
                        """)

                titleLayout.addWidget(i)
            # Create a QListWidgetItem to hold the custom widget
            list_item = QListWidgetItem(list_widget)
            list_item.setSizeHint(widget.sizeHint())

            # Set the custom widget as the item's widget
            list_widget.setItemWidget(list_item, widget)
            # self.mainLayout.addWidget(list_widget)
            self.labels.clear()
            self.percents.clear()
            self.pe.clear()
            for item in selectedWalls:
                widget = QWidget()
                layout = QHBoxLayout(widget)

                # Add labels
                label = QLabel(item["label"])
                percent = QDoubleSpinBox()
                percent.setRange(0, 100)
                percent.setValue(item["percent"])
                pe = QCheckBox()
                pe.setChecked(item["pe"])
                layout.addWidget(label)
                layout.addWidget(percent)
                layout.addWidget(pe)
                list_item = QListWidgetItem(list_widget)
                list_item.setSizeHint(widget.sizeHint())

                # Set the custom widget as the item's widget
                list_widget.setItemWidget(list_item, widget)
                self.mainLayout.addWidget(list_widget)
                self.labels.append(item["label"])
                self.percents.append(percent)
                self.pe.append(pe)
            self.selectedWalls = selectedWalls
            apply = QPushButton("Apply")
            apply.clicked.connect(self.apply)
            self.mainLayout.addWidget(apply)

        self.setLayout(self.mainLayout)

        return self.selectedWalls

    def next(self):
        # self.accept()
        self.selectedWalls.clear()
        for item in self.scene.selectedItems():
            for sh in self.shearWalls:
                mainItem = list(sh.keys())[0]
                mainItemValue = list(sh.values())[0]
                if mainItem == item and mainItemValue["story"] == self.Story:
                    self.selectedWalls.append(mainItemValue)
                    break

        list_widget = QListWidget(self)
        widget = QWidget()
        titleLayout = QHBoxLayout(widget)
        # Get the last widget in the layout and delete it
        self.delete_widget()
        self.delete_widget()
        if self.selectedWalls:
            # Add labels
            label = QLabel("Label")
            story = QLabel("Percentage")
            pe_title = QLabel("Transfer PE?")

            titles = [label, story, pe_title]
        else:
            label = QLabel(f"No selected walls!")
            titles = [label]
        for i in titles:
            i.setStyleSheet("""
                font-family: 'Arial';
                font-size:  14pt;
                font-weight: bold;
            """)

            titleLayout.addWidget(i)
        # Create a QListWidgetItem to hold the custom widget
        list_item = QListWidgetItem(list_widget)
        list_item.setSizeHint(widget.sizeHint())

        # Set the custom widget as the item's widget
        list_widget.setItemWidget(list_item, widget)
        self.mainLayout.addWidget(list_widget)
        self.labels.clear()
        self.percents.clear()
        self.pe.clear()
        for item in self.selectedWalls:
            widget = QWidget()
            layout = QHBoxLayout(widget)

            # Add labels
            label = QLabel(item["label"])
            percent = QDoubleSpinBox()
            percent.setRange(0, 100)
            pe = QCheckBox()
            pe.setChecked(False)
            layout.addWidget(label)
            layout.addWidget(percent)
            layout.addWidget(pe)
            list_item = QListWidgetItem(list_widget)
            list_item.setSizeHint(widget.sizeHint())

            # Set the custom widget as the item's widget
            list_widget.setItemWidget(list_item, widget)
            self.mainLayout.addWidget(list_widget)
            self.labels.append(item["label"])
            self.percents.append(percent)
            self.pe.append(pe)
            pe.checkStateChanged.connect(self.pe_check)

        apply = QPushButton("Apply")
        apply.clicked.connect(self.apply)
        self.mainLayout.addWidget(apply)

        self.setLayout(self.mainLayout)

    def apply(self):
        for i in range(len(self.labels)):
            self.selectedWalls[i]["percent"] = self.percents[i].value()
            self.selectedWalls[i]["pe"] = self.pe[i].isChecked()

        print(self.selectedWalls)
        self.accept()

    def pe_check(self):
        is_there_check = False
        for pe in self.pe:
            if pe.isChecked():
                is_there_check = True
                break
        if is_there_check:
            for pe in self.pe:
                if not pe.isChecked():
                    pe.setEnabled(False)
        else:
            for pe in self.pe:
                pe.setEnabled(True)

    def delete_widget(self):
        last_item = self.mainLayout.itemAt(self.mainLayout.count() - 1)
        if last_item:
            last_widget = last_item.widget()
            print(last_widget)
            if last_widget and (isinstance(last_widget, QListWidget) or isinstance(last_widget, QPushButton)):
                self.mainLayout.removeWidget(last_widget)
                last_widget.deleteLater()

    def wheelEvent(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.view.mapToScene(event.position().toPoint())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.view.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.view.mapToScene(event.position().toPoint())

        # Move scene to old position
        delta = newPos - oldPos
        self.view.translate(delta.x(), delta.y())


class Rectangle(QGraphicsRectItem):
    def __init__(self, x, y):
        super().__init__(x, y, 0, 0)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setPen(QPen(Qt.blue, 2))  # Set the border color to blue
        self.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))  # Set the fill color to transparent


class ShearWallStoryBy:
    def __init__(self, shearWalls, GridClass, story):
        print(shearWalls)
        # coordinate = [i["coordinate_main"] for i in shearWalls]
        # label = [i["label"] for i in shearWalls]
        # bending_dcr = [i["bending_dcr"] for i in shearWalls]
        # shear_dcr = [i["shear_dcr"] for i in shearWalls]
        # deflection_dcr = [i["deflection_dcr"] for i in shearWalls]
        self.view = None
        # instance = DrawShearWall()
        self.dialog = DrawShearWall(GridClass)
        self.dialog.story(story)

        self.view = self.dialog.view
        for shearWall in shearWalls:
            start = [float(i.strip()) * magnification_factor for i in shearWall["coordinate"][0][1:-1].split(",")]
            end = [float(i.strip()) * magnification_factor for i in shearWall["coordinate"][1][1:-1].split(",")]
            self.dialog.finalize_rectangle_copy(start, end, shearWall)
        self.dialog.Show()
        # self.dialog.show()
        self.result = self.dialog.exec()
