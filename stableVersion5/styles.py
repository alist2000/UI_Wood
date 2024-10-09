TabWidgetStyle = """
    QTabWidget {
        background-color: #F0F2F5; /* Light Grey */
        border: 1px solid #8395A7; /* Soft Slate Grey */
    }

    QTabBar::tab {
        background-color: #D9E1E8; /* Muted Blue */
        color: #3A3A3A; /* Charcoal Grey */
        padding: 8px 12px;
        margin: 1px;
        border: 1px solid #8395A7; /* Soft Slate Grey */
        border-radius: 4px;
    }

    QTabBar::tab:selected {
        background-color: #FFFFFF; /* White */
        border-bottom-color: #FFFFFF;
    }

    QWidget {
        background-color: #FFFFFF; /* White */
    }

    QPushButton {
        background-color: #5C80BC; /* Steel Blue */
        color: white;
        border: none;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: bold;
        border-radius: 4px;
    }

    QPushButton:hover {
        background-color: #6A91CC; /* Lighter Steel Blue */
    }

    QPushButton:pressed {
        background-color: #3A506B; /* Muted Blue */
    }

    QToolBar {
        background-color: #F0F2F5; /* Light Grey */
        border: none;
        spacing: 5px;
    }

    QToolBar > QToolButton {
        background-color: #5C80BC; /* Steel Blue */
        color: white;
        border: none;
        padding: 8px 16px;
        margin: 2px 0px;
        font-size: 14px;
        font-weight: bold;
        border-radius: 4px;
    }

    QToolBar > QToolButton:hover {
        background-color: #6A91CC; /* Lighter Steel Blue */
    }

    QToolBar > QToolButton:pressed {
        background-color: #3A506B; /* Muted Blue */
    }

    QToolBar > QToolButton:disabled {
        background-color: #CCCCCC; /* Light Grey for disabled */
        color: #666666;
    }
"""

menuStyle = """
    QMenuBar {
        background-color: #F0F2F5; /* Light Grey */
        border-bottom: 1px solid #8395A7; /* Soft Slate Grey */
    }

    QMenu {
        background-color: #FFFFFF; /* White */
        border: 1px solid #8395A7; /* Soft Slate Grey */
    }

    QMenu::item {
        padding: 8px 30px 8px 20px;
    }

    QMenu::item:selected {
        background-color: #5C80BC; /* Steel Blue */
        color: white;
    }

    QMenu::separator {
        height: 1px;
        background-color: #8395A7; /* Soft Slate Grey */
        margin: 4px 0px;
    }
"""

ButtonCheck = """
    QPushButton {
        background-color: #A8DF8E;
        color: black;
        border: none;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: bold;
        border-radius: 4px;
    }

    QPushButton:hover {
        background-color: #D0E7D2; 
        transform: translateY(-2px);
        
    }

    QPushButton:pressed {
        background-color: #B0D9B1;
        border-style: outset;
        transform: translateY(2px);    }

"""

ButtonUnCheck = """
    QPushButton {
        background-color: #5C80BC; /* Steel Blue */
        color: white;
        border: none;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: bold;
        border-radius: 4px;
    }

    QPushButton:hover {
        background-color: #6A91CC; /* Lighter Steel Blue */
    }

    QPushButton:pressed {
        background-color: #3A506B; /* Muted Blue */
    }
"""

tableStyle = """
    QTableWidget {
        gridline-color: transparent;
        border: 1px solid #8395A7; /* Soft Slate Grey */
    }

    QHeaderView::section {
        background-color: #F0F2F5; /* Light Grey */
        padding: 4px;
        border: 1px solid #8395A7; /* Soft Slate Grey */
        border-bottom: none;
        font-weight: bold;
    }

    QTableWidget::item {
        padding: 4px;
        border: none;
    }

    QTableWidget::item:selected {
        background-color: #D9E1E8; /* Muted Blue */
    }
"""
