from pathlib import Path


# Палитра цветов для темной темы (QPalette roles)
palette = {
    "Window": "#27231f",
    "WindowText": "#ead8bd",
    "Base": "#322c25",
    "Text": "#ead8bd",
    "Button": "#322c25",
    "ButtonText": "#ead8bd",
    "Highlight": "#e9ab48",
    "HighlightedText": "#27231f",
    "Mid": "#a4753f",
}


dark_style = """
QMainWindow, QDialog {
    background-color: #27231f;
    color: #ead8bd;
}
QLabel, QCheckBox, QGroupBox, QStatusBar {
    color: #ead8bd;
}
QTextBrowser {
    background-color: #322c25;
    color: #ead8bd;
    border: 1px solid #68513a;
    font-size: 14px;
    border-radius: 10px;
    padding: 8px;
}
QMenuBar {
    background-color: #322c25;
    color: #ead8bd;
}
QMenuBar::item {
    background-color: transparent;
}
QMenuBar::item:selected, QMenu::item:selected {
    background-color: #68513a;
}
QMenu {
    background-color: #322c25;
    color: #ead8bd;
    border: 1px solid #68513a;
}
QPushButton {
    background-color: #322c25;
    color: #ead8bd;
    border: 1px solid #68513a;
    border-radius: 5px;
    padding: 5px 10px;
}
QPushButton:hover:enabled {
    background-color: #443522;
    border: 1px solid #e9ab48;
    border-radius: 5px;
    padding: 5px 10px;
}
QPushButton:pressed:enabled {
    border: 1px solid #ba7a28;
    border-radius: 5px;
}
QLineEdit, QComboBox {
    background-color: #322c25;
    color: #ead8bd;
    border: 1px solid #68513a;
    border-radius: 5px;
    padding: 5px 10px;
}
QLineEdit:hover, QComboBox:hover:enabled {
    border: 1px solid #e9ab48;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #e9ab48;
    border-radius: 5px;
    padding: 5px 10px;
}
QComboBox QAbstractItemView, QTableWidget {
    background-color: #322c25;
    color: #ead8bd;
    border: 1px solid #68513a;
    selection-background-color: #ba7a28;
    selection-color: #ffffff;
    gridline-color: #68513a;
}
QHeaderView::section, QTableCornerButton::section {
    background-color: #27231f;
    color: #ead8bd;
    border: 1px solid #68513a;
    padding: 6px;
}
QGroupBox {
    border: 1px solid #68513a;
    border-radius: 5px;
    margin-top: 10px;
    padding: 18px 12px 12px 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
}
QPushButton:disabled, QComboBox:disabled, QMenu::item:disabled {
    color: #92816c;
    background-color: #302b25;
}

QWidget#centralwidget, QWidget#controlsPanel {
    background-color: #27231f;
}
QStatusBar {
    background-color: #27231f;
    color: #ead8bd;
    border-top: 1px solid #68513a;
    padding: 3px 12px;
    min-height: 22px;
}
QStatusBar::item {
    border: none;
}
QLabel#titleLabel {
    font-size: 19px;
    font-weight: 600;
    padding-bottom: 10px;
}
QLabel#sourceLabel, QLabel#logLabel {
    font-weight: 600;
}
QPushButton, QLineEdit, QComboBox {
    min-height: 20px;
    font-size: 13px;
}
QComboBox {
    padding-right: 30px;
}
QComboBox:hover:enabled, QComboBox:focus {
    padding-right: 30px;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 26px;
    border: none;
}
QComboBox::down-arrow {
    image: url(ARROW_PATH);
    width: 12px;
    height: 8px;
}
QCheckBox {
    spacing: 8px;
    min-height: 24px;
    padding: 2px 0;
}

QScrollArea#mapScroll, QScrollArea#mapScroll > QWidget > QWidget {
    background: transparent;
    border: none;
}
QStatusBar {
    background-color: #382b1b;
    color: #f4c879;
    border-top: 1px solid #9a6c32;
    padding: 5px 14px;
    min-height: 24px;
    font-size: 12px;
}
QComboBox:hover:enabled, QComboBox:focus, QComboBox:on {
    background-color: #49351f;
    color: #ffe4b3;
    border: 1px solid #e9ab48;
}
QComboBox::drop-down:hover, QComboBox::drop-down:on {
    background-color: #a76520;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}
QComboBox QAbstractItemView {
    selection-background-color: #a76520;
    selection-color: #ffffff;
    outline: none;
}
QComboBox QAbstractItemView::item {
    min-height: 28px;
    padding: 3px 8px;
}
QComboBox QAbstractItemView::item:hover, QComboBox QAbstractItemView::item:selected {
    background-color: #a76520;
    color: #ffffff;
}

QFrame#mapFrame {
    border-radius: 11px;
    border: 1px solid #a4753f;
}
QLabel#imageLabel {
    border: none;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #c49a61;
    border-radius: 3px;
    background-color: #322c25;
}
QCheckBox::indicator:hover {
    border: 1px solid #e9ab48;
}
QCheckBox::indicator:checked {
    background-color: #a76520;
    border: 1px solid #a76520;
    image: url(CHECK_PATH);
}
"""

dark_style = dark_style.replace("ARROW_PATH", (Path(__file__).parent / "arrow_dark.svg").as_posix())

dark_style = dark_style.replace("CHECK_PATH", (Path(__file__).parent / "check.svg").as_posix())
