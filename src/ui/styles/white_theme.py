from pathlib import Path


# Палитра цветов для светлой темы (QPalette roles)
palette = {
    "Window": "#eef5ff",
    "WindowText": "#243b5a",
    "Base": "#ffffff",
    "Text": "#243b5a",
    "Button": "#e0edff",
    "ButtonText": "#243b5a",
    "Highlight": "#2878c8",
    "HighlightedText": "#ffffff",
    "Mid": "#83a9d5",
}


light_style = """
QMainWindow, QDialog {
    background-color: #eef5ff;
    color: #243b5a;
}
QLabel, QCheckBox, QGroupBox, QStatusBar {
    color: #243b5a;
}
QTextBrowser {
    background-color: #ffffff;
    color: #243b5a;
    border: 1px solid #b6cbe5;
    font-size: 14px;
    border-radius: 10px;
    padding: 8px;
}
QMenuBar {
    background-color: #e0edff;
    color: #243b5a;
}
QMenuBar::item {
    background-color: transparent;
}
QMenuBar::item:selected {
    background-color: #c4defb;
}
QMenu {
    background-color: #ffffff;
    color: #243b5a;
    border: 1px solid #b6cbe5;
}
QMenu::item:selected {
    background-color: #2878c8;
    color: #ffffff;
}
QPushButton {
    background-color: #e0edff;
    color: #243b5a;
    border: 1px solid #a6bfdc;
    border-radius: 5px;
    padding: 5px 10px;
}
QPushButton:hover:enabled {
    background-color: #d7e9ff;
    background-color: #d7e9ff;
    border: 1px solid #2878c8;
    border-radius: 5px;
    padding: 5px 10px;
}
QPushButton:pressed:enabled {
    background-color: #c4defb;
    border: 1px solid #1a5eab;
    border-radius: 5px;
}
QLineEdit, QComboBox {
    background-color: #ffffff;
    color: #243b5a;
    border: 1px solid #a6bfdc;
    border-radius: 5px;
    padding: 5px 10px;
}
QLineEdit:hover, QComboBox:hover:enabled {
    border: 1px solid #2878c8;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #2878c8;
    border-radius: 5px;
    padding: 5px 10px;
}
QComboBox QAbstractItemView, QTableWidget {
    background-color: #ffffff;
    color: #243b5a;
    border: 1px solid #b6cbe5;
    selection-background-color: #2878c8;
    selection-color: #ffffff;
    gridline-color: #b6cbe5;
}
QHeaderView::section, QTableCornerButton::section {
    background-color: #e0edff;
    color: #243b5a;
    border: 1px solid #b6cbe5;
    padding: 6px;
}
QGroupBox {
    border: 1px solid #a6bfdc;
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
    color: #777777;
    background-color: #e0edff;
}

QWidget#centralwidget, QWidget#controlsPanel {
    background-color: #eef5ff;
}
QStatusBar {
    background-color: #eef5ff;
    color: #243b5a;
    border-top: 1px solid #b6cbe5;
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
    background-color: #dceaff;
    color: #204e83;
    border-top: 1px solid #83a9d5;
    padding: 5px 14px;
    min-height: 24px;
    font-size: 12px;
}
QComboBox:hover:enabled, QComboBox:focus, QComboBox:on {
    background-color: #d7eaff;
    color: #174a80;
    border: 1px solid #3498db;
}
QComboBox::drop-down:hover, QComboBox::drop-down:on {
    background-color: #2878c8;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}
QComboBox QAbstractItemView {
    selection-background-color: #2878c8;
    selection-color: #ffffff;
    outline: none;
}
QComboBox QAbstractItemView::item {
    min-height: 28px;
    padding: 3px 8px;
}
QComboBox QAbstractItemView::item:hover, QComboBox QAbstractItemView::item:selected {
    background-color: #2878c8;
    color: #ffffff;
}

QFrame#mapFrame {
    border-radius: 11px;
    border: 1px solid #83a9d5;
}
QLabel#imageLabel {
    border: none;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #6384aa;
    border-radius: 3px;
    background-color: #ffffff;
}
QCheckBox::indicator:hover {
    border: 1px solid #3498db;
}
QCheckBox::indicator:checked {
    background-color: #2878c8;
    border: 1px solid #2878c8;
    image: url(CHECK_PATH);
}
"""

light_style = light_style.replace("ARROW_PATH", (Path(__file__).parent / "arrow_light.svg").as_posix())

light_style = light_style.replace("CHECK_PATH", (Path(__file__).parent / "check.svg").as_posix())
