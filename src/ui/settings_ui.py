import io
from pathlib import Path

from PyQt6 import uic, QtWidgets

from src.ui.ui import settings_ui


fuels = ("АИ-92", "АИ-95", "ДТ", "Газ", "АИ-98")


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, selected, directory, file_format, theme, parent=None):
        super().__init__(parent)
        uic.loadUi(io.StringIO(settings_ui), self)

        self.fuel_checks = dict(zip(fuels, (
            self.ai92Check, self.ai95Check, self.dieselCheck, self.gasCheck, self.ai98Check
        )))

        for fuel, checkbox in self.fuel_checks.items():
            checkbox.setChecked(fuel in selected)
            checkbox.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)

        self.directory_edit.setText(directory)
        self.format_box.setCurrentText(file_format)
        self.theme_box.setItemData(0, "dark")
        self.theme_box.setItemData(1, "light")
        self.theme_box.setCurrentIndex(self.theme_box.findData(theme))
        self.error_label.hide()
        self.browse_button.clicked.connect(self.choose_directory)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        for combo in (self.format_box, self.theme_box):
            combo.setView(QtWidgets.QListView(combo))
            combo.view().setMouseTracking(True)

        for widget in (self.directory_edit, self.format_box, self.theme_box,
                       *self.findChildren(QtWidgets.QPushButton)):
            widget.setFixedHeight(32)

    # выбор папки (не файла)
    def choose_directory(self):
        start = self.directory_edit.text().strip()

        if start == "":
            start = str(Path.home())

        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Папка результатов", start)

        if folder != "":
            self.directory_edit.setText(folder)

    def selected_fuels(self):
        return [fuel for fuel, checkbox in self.fuel_checks.items() if checkbox.isChecked()]

    def accept(self):
        if not self.selected_fuels():
            self.error_label.setText("Выберите хотя бы один вид топлива.")
            self.error_label.show()
            return

        directory = self.directory_edit.text().strip()

        if not directory or not Path(directory).expanduser().is_dir():
            self.error_label.setText("Укажите существующую папку для результатов.")
            self.error_label.show()
            return

        self.directory_edit.setText(str(Path(directory).expanduser().resolve()))
        super().accept()
