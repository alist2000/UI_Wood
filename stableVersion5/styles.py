TabWidgetStyle = """
            QTabWidget {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255,   255,   255,   255), stop:1 rgba(247,   247,   247,   255));
                border:   1px solid #C0C0C0;
            }
            
            QTabBar::tab {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255,   255,   255,   255), stop:1 rgba(255,   255,   255,   255));
                padding:   10px;
                margin:   2px;
                border:   1px solid #C0C0C0;
                border-radius:  4px;

            }
            
            QTabBar::tab:selected {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255,   255,   255,   255), stop:1 rgba(236,   236,   236,   255));
                border:   1px solid #9B9B9B;
            }
            
            QWidget {
                background-color: white;
            }
            
            QPushButton {
                background-color: #C7C8CC; 
                border: none;
                color: black;
                text-align: center;
                display: inline-block;
                font-size:   14px;
                margin:   4px   2px;
                cursor: pointer;
                padding:   4px   16px;
                text-decoration: none;
                border-radius:  4px;
                box-shadow:  0  4px  8px  0 rgba(0,  0,  0,  0.2),  0  6px  20px  0 rgba(0,  0,  0,  0.19);
            }
            
            QPushButton:hover {
                background-color: #CEE6F3;
                transform: translateY(-2px);
            }
            
            QPushButton:pressed {
                background-color: #B7C4CF;
                border-style: outset;
                transform: translateY(2px);
            }
                    QToolBar {
                background-color: #f8f9fa;
                border: none;
                spacing:  5px;
            }
            
            QToolBar > QToolButton {
                background-color: #EEEEEE; 
                border: none;
                color: black;
                text-align: center;
                display: inline-block;
                font-size:   14px;
                margin:   1px   1px;
                cursor: pointer;
                padding:   4px   15px;
                text-decoration: none;
                border-radius:   3px;
                box-shadow:   0   4px   8px   0 rgba(0,   0,   0,   0.2),   0   6px   20px   0 rgba(0,   0,   0,   0.19);
            }
            
            QToolBar > QToolButton:hover {
                background-color: #CDE8F6;
                transform: translateY(-2px);
            }
            
            QToolBar > QToolButton:pressed {
                background-color: #B7C4CF;
                border-style: outset;
                transform: translateY(2px);
            }
            QToolBar > QToolButton:disabled {
                  background-color: #cccccc; /* Gray background for disabled buttons */
                  color: #666666; /* Dark gray text for disabled buttons */
                  cursor: not-allowed; /* Changes the cursor to indicate that the button cannot be interacted with */
                }
        """

menuStyle = """
            QMenuBar {
                background-color: #f8f9fa;
                border: none;
            }
            
            QMenu {
                background-color: #ffffff;
                border:  1px solid #ced4da;
            }
            QAction {
                padding:   5px   30px   5px   20px;
                background-color: transparent;
                color: #495057;
            }
            
            QAction:hover {
                background-color: #f8f9fa;
                color: #495057;
            }
            
            QAction:checked {
                background-color: #007bff;
                color: white;
            }
            
            QAction:disabled {
                color: #6c757d;
            }
            
            QMenu::item {
                padding:  5px  30px  5px  20px;
            }
            
            QMenu::item:selected {
                background-color: #007bff;
                color: white;
            }
            
            QMenu::item:disabled {
                color: #6c757d;
            }
            
            QMenu::separator {
                height:  1px;
                background-color: #ced4da;
                margin-left:  5px;
                margin-right:  5px;
            }
            QMenu::item:hover {
                background-color: #007bff;
                color: white;
            }
            
            QMenu::item:checked {
                background-color: #007bff;
                color: white;
            }
        """

tableStyle = """
            QTableWidget {
                gridline-color: transparent;
                border:  1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #f1f1f1;
                padding:  4px;
                border:  1px solid #ddd;
                border-bottom: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding:  4px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #dcf4fc;
            }
        """
