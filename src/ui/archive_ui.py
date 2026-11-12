import io
from PyQt6 import uic, QtCore, QtWidgets

from src.ui.ui import archive_ui
from src.db import list_runs, delete_run


class ArchiveDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(io.StringIO(archive_ui), self)

        self.selected_id = None

        # режимы колонок задаём один раз: дата и источник по содержимому, АЗС занимает остаток
        self.table.setColumnCount(3)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setHighlightSections(False)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.open_button.setFixedHeight(32)
        self.delete_button.setFixedHeight(32)
        self.close_button.setFixedHeight(32)

        self.open_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        self.open_button.clicked.connect(self._open)
        self.delete_button.clicked.connect(self._delete)
        self.close_button.clicked.connect(self.reject)
        self.table.itemSelectionChanged.connect(self._on_select)
        self.table.itemDoubleClicked.connect(self._open)

        self._fill()

    def _fill(self):
        runs = list_runs()
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(["Дата", "Источник", "АЗС"])

        for run in runs:
            row = self.table.rowCount()
            self.table.insertRow(row)

            created = run["created_at"]
            if "T" in created:
                created = created.replace("T", " ")
            if "." in created:
                created = created.split(".")[0]

            date_item = QtWidgets.QTableWidgetItem(created)
            source_item = QtWidgets.QTableWidgetItem(run["source"])
            count_item = QtWidgets.QTableWidgetItem(str(run["stations_count"]))

            date_item.setData(QtCore.Qt.ItemDataRole.UserRole, run["id"])

            self.table.setItem(row, 0, date_item)
            self.table.setItem(row, 1, source_item)
            self.table.setItem(row, 2, count_item)

    def _on_select(self):
        enabled = len(self.table.selectedItems()) > 0
        self.open_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

        if enabled:
            item = self.table.item(self.table.currentRow(), 0)
            self.selected_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        else:
            self.selected_id = None

    def _open(self):
        if self.selected_id is None:
            return
        self.accept()

    def _delete(self):
        if self.selected_id is None:
            return
        delete_run(self.selected_id)
        self.selected_id = None
        self._fill()
        self.open_button.setEnabled(False)
        self.delete_button.setEnabled(False)