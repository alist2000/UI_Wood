from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QDialogButtonBox
from UI_Wood.stableVersion5.replicate import CheckableComboBox
from UI_Wood.stableVersion5.styles import TabWidgetStyle



class Delete:
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
        self.dialog.setWindowTitle("Delete")
        self.dialog.setStyleSheet(TabWidgetStyle)

        self.layout = QVBoxLayout()

        # Set up combo box 1
        # Set up combo box 2
        self.label2 = QLabel("Stories:")
        self.target_story = CheckableComboBox()
        self.target_story.addItems([f"Story{i + 1}" for i in range(len(self.mainPage.mainPage.grid))])
        selectAllButton = QCheckBox("Select/Deselect")
        selectAllButton.stateChanged.connect(self.target_story.selectDeselectAll)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.label2)
        h_layout.addWidget(selectAllButton)

        # Set up check boxes
        self.checkbox_post = QCheckBox("Post")
        self.checkbox_beam = QCheckBox("Beam")
        self.checkbox_joist = QCheckBox("Joist")
        self.checkbox_shearWall = QCheckBox("Shear Wall")
        self.checkbox_studWall = QCheckBox("Stud Wall")
        self.checkbox_loadMap = QCheckBox("Load Map")
        self.checkbox_selectedObject = QCheckBox("Selected Objects")

        # Add labels, combo boxes and check boxes to layout
        # self.layout.addWidget(self.label2)
        self.layout.addLayout(h_layout)
        self.layout.addWidget(self.target_story)
        self.layout.addWidget(self.checkbox_post)
        self.layout.addWidget(self.checkbox_beam)
        self.layout.addWidget(self.checkbox_joist)
        self.layout.addWidget(self.checkbox_shearWall)
        self.layout.addWidget(self.checkbox_studWall)
        self.layout.addWidget(self.checkbox_loadMap)
        self.layout.addWidget(self.checkbox_selectedObject)

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
        targetTabIndexes = [int(i[-1]) - 1 for i in self.target_story.currentData()]
        copy_list_item = ["post", "beam", "joist", "shearWall", "studWall", "loadMap", "Selected Objects"]
        item_selected = []
        for i, item in enumerate([self.checkbox_post, self.checkbox_beam, self.checkbox_joist, self.checkbox_shearWall,
                                  self.checkbox_studWall, self.checkbox_loadMap, self.checkbox_selectedObject]):
            if item.isChecked():
                item_selected.append(copy_list_item[i])
        DeleteObject(targetTabIndexes, self.mainPage.mainPage.grid, item_selected)

        self.dialog.accept()


class DeleteObject:
    def __init__(self, targetTabIndex, grid, items):

        for i in targetTabIndex:
            sourceTab = grid[i]
            selectedItems = sourceTab.scene.selectedItems()
            postObjects = sourceTab.post_instance.post_prop
            beamObjects = sourceTab.beam_instance.beam_rect_prop
            joistObjects = sourceTab.joist_instance.rect_prop
            shearWallObjects = sourceTab.shearWall_instance.shearWall_rect_prop
            studWallObjects = sourceTab.studWall_instance.studWall_rect_prop
            loadMapObjects = sourceTab.load_instance.rect_prop
            for item in items:
                if item == "post":
                    for postObject, postProp in list(postObjects.items()):
                        try:
                            sourceTab.snapPoint.remove_point(postProp["coordinate"])
                        except:
                            pass
                        del postObject.post_prop[postObject]
                        sourceTab.scene.removeItem(postObject)
                elif item == "beam":
                    for beamObject, beamProp in list(beamObjects.items()):
                        try:
                            sourceTab.snapPoint.remove_point(beamProp["coordinate"][0])
                            sourceTab.snapPoint.remove_point(beamProp["coordinate"][1])
                            sourceTab.snapLine.remove_line(tuple(beamProp["coordinate"]))
                        except:
                            pass
                        del beamObject.rect_prop[beamObject]
                        sourceTab.scene.removeItem(beamObject)
                elif item == "joist":
                    for joistObject, joistProp in list(joistObjects.items()):
                        for point in joistProp["coordinate"]:
                            try:
                                sourceTab.snapPoint.remove_point(point)
                            except:
                                pass
                        del joistObject.rect_prop[joistObject]
                        sourceTab.scene.removeItem(joistObject)
                elif item == "shearWall":
                    for shearWallObject, shearWallProp in list(shearWallObjects.items()):
                        # delete snap points (start & end)
                        try:
                            sourceTab.snapPoint.remove_point(shearWallProp["post"]["start_center"])
                            sourceTab.snapPoint.remove_point(shearWallProp["post"]["end_center"])
                        except:
                            pass

                        # delete start and end rectangles
                        if type(shearWallProp["post"]["start_rect_item"]) is not str:
                            sourceTab.scene.removeItem(shearWallProp["post"]["start_rect_item"])
                            sourceTab.scene.removeItem(shearWallProp["post"]["end_rect_item"])
                            # delete item
                        del shearWallObject.rect_prop[shearWallObject]
                        sourceTab.scene.removeItem(shearWallObject)

                elif item == "studWall":
                    for studWallObject, studWallProp in list(studWallObjects.items()):
                        try:
                            sourceTab.snapPoint.remove_point(studWallProp["coordinate"][0])
                            sourceTab.snapPoint.remove_point(studWallProp["coordinate"][1])
                            sourceTab.snapLine.remove_line(tuple(studWallProp["coordinate"]))
                        except:
                            pass
                        del studWallObject.rect_prop[studWallObject]
                        sourceTab.scene.removeItem(studWallObject)

                elif item == "loadMap":
                    for loadMapObject, loadProp in list(loadMapObjects.items()):
                        for point in loadProp["coordinate"]:
                            try:
                                sourceTab.snapPoint.remove_point(point)
                            except:
                                pass
                        del loadMapObject.rect_prop[loadMapObject]
                        sourceTab.scene.removeItem(loadMapObject)

                elif item == "Selected Objects":
                    for selectedItem in selectedItems:
                        elementName = selectedItem.elementName
                        if elementName == "post":
                            try:
                                sourceTab.snapPoint.remove_point(selectedItem.post_prop[selectedItem]["coordinate"])
                            except:
                                pass
                            del selectedItem.post_prop[selectedItem]
                            sourceTab.scene.removeItem(selectedItem)

                        elif elementName == "beam":
                            # HOW TO DELETE JUST ONE OBJECT.
                            try:
                                sourceTab.snapPoint.remove_point(selectedItem.rect_prop[selectedItem]["coordinate"][0])
                                sourceTab.snapPoint.remove_point(selectedItem.rect_prop[selectedItem]["coordinate"][1])
                                sourceTab.snapLine.remove_line(
                                    tuple(selectedItem.rect_prop[selectedItem]["coordinate"]))
                            except:
                                pass
                            del selectedItem.rect_prop[selectedItem]
                            sourceTab.scene.removeItem(selectedItem)

                        elif elementName == "joist":
                            for point in selectedItem.rect_prop[selectedItem]["coordinate"]:
                                try:
                                    sourceTab.snapPoint.remove_point(point)
                                except:
                                    pass
                            del selectedItem.rect_prop[selectedItem]
                            sourceTab.scene.removeItem(selectedItem)

                        elif elementName == "shearWall":
                            # delete snap points (start & end)
                            try:
                                sourceTab.snapPoint.remove_point(
                                    selectedItem.rect_prop[selectedItem]["post"]["start_center"])
                                sourceTab.snapPoint.remove_point(
                                    selectedItem.rect_prop[selectedItem]["post"]["end_center"])
                            except:
                                pass

                            # delete start and end rectangles
                            if type(selectedItem.rect_prop[selectedItem]["post"]["start_rect_item"]) is not str:
                                sourceTab.scene.removeItem(
                                    selectedItem.rect_prop[selectedItem]["post"]["start_rect_item"])
                                sourceTab.scene.removeItem(
                                    selectedItem.rect_prop[selectedItem]["post"]["end_rect_item"])
                            # delete item
                            del selectedItem.rect_prop[selectedItem]
                            sourceTab.scene.removeItem(selectedItem)

                        elif elementName == "studWall":
                            try:
                                sourceTab.snapPoint.remove_point(selectedItem.rect_prop[selectedItem]["coordinate"][0])
                                sourceTab.snapPoint.remove_point(selectedItem.rect_prop[selectedItem]["coordinate"][1])
                                sourceTab.snapLine.remove_line(
                                    tuple(selectedItem.rect_prop[selectedItem]["coordinate"]))
                            except:
                                pass
                            del selectedItem.rect_prop[selectedItem]
                            sourceTab.scene.removeItem(selectedItem)

                        elif elementName == "loadMap":
                            for point in selectedItem.rect_prop[selectedItem]["coordinate"]:
                                try:
                                    sourceTab.snapPoint.remove_point(point)
                                except:
                                    pass
                            del selectedItem.rect_prop[selectedItem]
                            sourceTab.scene.removeItem(selectedItem)
