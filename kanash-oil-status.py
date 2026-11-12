import csv
import io
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from PyQt6 import uic, QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QHeaderView

from src import paths
from src.parsers import gis2, sber, tbank, parser
from src.map import map_painter
from src.ui import ui
from src.ui.archive_ui import ArchiveDialog
from src.ui.settings_ui import fuels, SettingsDialog
from src.db import save_run, list_runs, load_rows
from src.ui.styles.dark_theme import dark_style, palette as dark_palette
from src.ui.styles.white_theme import light_style, palette as light_palette


APP_VERSION = "1.0.0"

# источники
sources = (
    ("2gis", gis2.fetch, parser.normalize_gis2),
    ("tbank", tbank.fetch, parser.normalize_tbank),
    ("sber", sber.fetch, parser.normalize_sber),
)

# кастомный шрифт (iter)
def load_fonts(app):
    folder = paths.resource_dir() / "src" / "fonts"

    for path in sorted(folder.glob("*.otf")):
        QtGui.QFontDatabase.addApplicationFont(str(path))

    font = app.font()
    font.setFamily("Inter")
    app.setFont(font)


# колонки таблицы
def table_header(selected_fuels):
    return ["Название", "Адрес"] + list(selected_fuels)


# строки таблицы
def table_rows(rows, selected_fuels):
    body = []

    for row in rows:
        line = [row["name"], row["address"]]

        for fuel in selected_fuels:
            line.append(parser.labels[row["fuels"][fuel]])

        body.append(line)

    return body


def write_csv(path, header, body):
    with open(path, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        writer.writerows(body)


def write_xlsx(path, header, body):
    book = Workbook()
    sheet = book.active
    sheet.title = "АЗС"

    header_fill = PatternFill(
        start_color="4472C4", end_color="4472C4", fill_type="solid"
    )
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alignment = Alignment(horizontal="center", vertical="center")
    cell_alignment = Alignment(horizontal="center", vertical="center")

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    # цвета ячеек
    colors = {
        "Есть": "C6EFCE",
        "Нет": "FFC7CE",
        "Возможно": "FFEB9C",
        "Н/Д": "D9D9D9",
    }

    # запись
    sheet.append(header)
    for col_idx in range(1, len(header) + 1):
        cell = sheet.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    for r, line in enumerate(body):
        sheet.append(line)
        row_idx = r + 2

        for c in range(len(header)):
            cell = sheet.cell(row=row_idx, column=c + 1)
            cell.border = thin_border

            # название и адрес
            if c < 2:
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.alignment = cell_alignment
                # статус
                color = colors.get(str(cell.value))
                if color is not None:
                    cell.fill = PatternFill("solid", start_color=color)

    # ширина столбцов
    sheet.column_dimensions["A"].width = 34
    sheet.column_dimensions["B"].width = 60

    for number in range(3, len(header) + 1):
        sheet.column_dimensions[get_column_letter(number)].width = 14

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions

    book.save(path)


class MainWindow(QMainWindow):
    # создает окно и грузит все нужное
    def __init__(self):
        super().__init__()

        # настройки (ini-файл в папке пользователя, а не реестр Windows)
        settings_path = paths.writable_dir() / "settings.ini"
        self.settings = QtCore.QSettings(str(settings_path), QtCore.QSettings.Format.IniFormat)
        saved = self.settings.value("fuels", list(fuels[:4]), type=list)
        self.fuels = [f for f in fuels if f in saved] or list(fuels[:4])
        self.directory = str(self.settings.value(
            "directory", str(paths.writable_dir() / "results")))
        self.file_format = str(self.settings.value("format", "CSV"))

        if self.file_format not in ("CSV", "XLSX"):
            self.file_format = "CSV"

        self.theme = str(self.settings.value("theme", "dark"))

        if self.theme not in ("dark", "light"):
            self.theme = "dark"

        # загрузка интерфейсв
        uic.loadUi(io.StringIO(ui.UI), self)
        QApplication.instance().setStyle("Fusion")
        self.sourceBox.setView(QtWidgets.QListView(self.sourceBox))
        self.sourceBox.view().setMouseTracking(True)

        for w in (self.sourceBox, self.startButton, self.stopButton,
                  self.settingsButton, self.archiveButton, self.openTableButton):
            w.setFixedHeight(32)

        # скрытая кнопка (после парсинга появляется)
        policy = self.openTableButton.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.openTableButton.setSizePolicy(policy)
        self.setMinimumSize(780, 560)

        # состояния
        self.running = False
        self.finished = False
        self.rows = []
        self.source_code = ""
        self.job = None
        self.table_dialog = None

        self.setup_menu()
        self.apply_theme()
        self.setup_alt_menu()

        # привязка кнопок
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.archiveButton.clicked.connect(self.open_archive)
        self.openTableButton.clicked.connect(self.open_table)
        self.settingsButton.clicked.connect(self.open_settings)

        # карта
        self.map_pixmap = QtGui.QPixmap(str(paths.resource_dir() / "src" / "map" / "map_clean.png"))
        self.resize_map()
        self.initial_size = self.size()
        self.setFixedSize(self.initial_size)
        self.statusbar.setSizeGripEnabled(False)

        # на старте все точки серые (карта без данных)
        self.draw_map([], [])

        self.statusbar.showMessage("Готово · Источник: " + self.sourceBox.currentText())

    # подгоняет карту под экран (нейронка)
    def resize_map(self):
        if self.map_pixmap.isNull():
            return

        screen = self.screen().availableGeometry()
        size = QtCore.QSize(max(320, screen.width() - 340), max(220, screen.height() - 300))
        size = size.boundedTo(self.map_pixmap.size())
        pixmap = self.map_pixmap.scaled(
            size, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation)

        # скругляем углы
        rounded = QtGui.QPixmap(pixmap.size())
        rounded.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(rounded)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(pixmap.rect()), 10, 10)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        self.imageLabel.setPixmap(rounded)
        self.imageLabel.setFixedSize(pixmap.size())
        self.mapFrame.setFixedSize(pixmap.width() + 2, pixmap.height() + 2)
        self.resize(pixmap.width() + 304, pixmap.height() + 260)

    # настраивает меню для мака
    def setup_menu(self):
        for action in self.findChildren(QtGui.QAction):
            action.setMenuRole(QtGui.QAction.MenuRole.NoRole)
        self.actionExit.setMenuRole(QtGui.QAction.MenuRole.QuitRole)

        # привязка менюбара
        self.actionClose.triggered.connect(self.close)
        self.actionExit.triggered.connect(QApplication.instance().quit)
        self.actionStatusBar.toggled.connect(self.statusbar.setVisible)
        self.actionFullScreen.toggled.connect(self.set_full_screen)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionHelp.triggered.connect(self.show_help)
        self.actionStart.triggered.connect(self.start)
        self.actionStop.triggered.connect(self.stop)
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionTheme.triggered.connect(self.change_theme)
        self.actionSave.triggered.connect(self.export_current)
        self.actionOpen.triggered.connect(self.open_table)
        self.actionArchive.triggered.connect(self.open_archive)
        self.actionArchive.setEnabled(True)

        # источники, выбираем 1 (по умолчанию 2гис)
        self.sourceActions = QtGui.QActionGroup(self)
        self.sourceActions.setExclusive(True)
        actions = (self.actionSource2GIS, self.actionSourceTBank, self.actionSourceSber)

        for i, action in enumerate(actions):
            self.sourceActions.addAction(action)
            action.triggered.connect(lambda checked, i=i: self.sourceBox.setCurrentIndex(i))

        # список к меню
        self.sourceBox.currentIndexChanged.connect(self.sync_source_menu)
        self.sync_source_menu(self.sourceBox.currentIndex())

    # на винде меню скрыто и открывается по альту
    def setup_alt_menu(self):
        self.alt_menu = sys.platform == "win32"
        self.alt_pressed_alone = False
        if not self.alt_menu:
            return

        self.menuBar().setVisible(False)
        QApplication.instance().installEventFilter(self)

        # после закрытия любого меню прячем строку меню
        for menu in self.menuBar().findChildren(QtWidgets.QMenu):
            menu.aboutToHide.connect(
                lambda: QtCore.QTimer.singleShot(150, self.hide_menubar_if_idle))

    def window_size_for_menubar(self):
        size = QtCore.QSize(self.initial_size)
        if self.alt_menu and self.menuBar().isVisible():
            size.setHeight(size.height() + self.menuBar().sizeHint().height())
        return size

    def set_menubar_visible(self, visible):
        bar = self.menuBar()
        if bar.isVisible() == visible:
            return

        bar.setVisible(visible)
        if not (self.isFullScreen() or self.isMaximized()):
            self.setFixedSize(self.window_size_for_menubar())

        if visible:
            actions = bar.actions()
            if actions:
                bar.setFocus()
                bar.setActiveAction(actions[0])

    def hide_menubar_if_idle(self):
        if QApplication.activePopupWidget() is None:
            self.set_menubar_visible(False)

    def eventFilter(self, obj, event):
        if getattr(self, "alt_menu", False) and QApplication.activeWindow() is self:
            kind = event.type()
            key = event.key() if hasattr(event, "key") else None
            bar = self.menuBar()

            if kind == QtCore.QEvent.Type.KeyPress:
                if key == QtCore.Qt.Key.Key_Alt:
                    self.alt_pressed_alone = not event.isAutoRepeat()
                else:
                    self.alt_pressed_alone = False
                    if (key == QtCore.Qt.Key.Key_Escape and bar.isVisible()
                            and QApplication.activePopupWidget() is None):
                        self.set_menubar_visible(False)

            elif kind == QtCore.QEvent.Type.KeyRelease:
                if key == QtCore.Qt.Key.Key_Alt and self.alt_pressed_alone:
                    self.alt_pressed_alone = False
                    self.set_menubar_visible(not bar.isVisible())

            elif kind == QtCore.QEvent.Type.MouseButtonPress:
                if bar.isVisible() and QApplication.activePopupWidget() is None:
                    widget = QApplication.widgetAt(QtGui.QCursor.pos())
                    if widget is None or not (widget is bar or bar.isAncestorOf(widget)):
                        self.set_menubar_visible(False)

        return super().eventFilter(obj, event)

    # применяет тему
    def apply_theme(self):
        app = QApplication.instance()
        palette = app.style().standardPalette()

        if self.theme == "dark":
            colors = dark_palette
            app.setStyleSheet(dark_style)
            self.actionTheme.setText("Светлая тема")

        else:
            colors = light_palette
            app.setStyleSheet(light_style)
            self.actionTheme.setText("Тёмная тема")

        for name in ("Window", "WindowText", "Base", "Text", "Button",
                     "ButtonText", "Highlight", "HighlightedText", "Mid"):
            palette.setColor(getattr(QtGui.QPalette.ColorRole, name), QtGui.QColor(colors[name]))

        app.setPalette(palette)

    # сохраняет настройки
    def save_settings(self):
        self.settings.setValue("fuels", self.fuels)
        self.settings.setValue("directory", self.directory)
        self.settings.setValue("format", self.file_format)
        self.settings.setValue("theme", self.theme)
        self.settings.sync()

        if self.settings.status() != QtCore.QSettings.Status.NoError:
            QtWidgets.QMessageBox.warning(
                self, "Настройки", "Не удалось сохранить настройки на диск. "
                "В текущем сеансе они применены, но могут потеряться после закрытия.")

    # смена темы
    def change_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()
        self.save_settings()

    # настройки
    def open_settings(self):
        if self.running:
            return

        dialog = SettingsDialog(self.fuels, self.directory, self.file_format, self.theme, self)

        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        fuels = dialog.selected_fuels()

        # таблица перестроится при открытии, парсить заново не надо
        changed = fuels != self.fuels

        if dialog.format_box.currentText() != self.file_format:
            changed = True

        if changed and self.table_dialog is not None:
            self.table_dialog.close()

        self.fuels = fuels
        self.directory = dialog.directory_edit.text()
        self.file_format = dialog.format_box.currentText()
        self.theme = dialog.theme_box.currentData()
        self.apply_theme()
        self.save_settings()
        self.update_controls()
        self.append_log("Настройки сохранены.")

    # синхронизация менюбара
    def sync_source_menu(self, index):
        self.sourceActions.actions()[index].setChecked(True)
        self.statusbar.showMessage("Готово · Источник: " + self.sourceBox.currentText())
        self.finished = False
        self.rows = []
        self.update_controls()

        if self.table_dialog is not None:
            self.table_dialog.close()

        self.append_log("Выбран источник: " + self.sourceBox.currentText())

    # логи
    def append_log(self, text):
        time = QtCore.QTime.currentTime().toString("HH:mm:ss")
        cursor = self.logBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)

        if not self.logBrowser.document().isEmpty():
            cursor.insertBlock()

        cursor.insertText(f'[{time}] "{text}"')
        self.logBrowser.setTextCursor(cursor)
        self.logBrowser.ensureCursorVisible()

    # включает и выключает кнопки
    def update_controls(self):
        idle = not self.running
        self.startButton.setEnabled(idle)
        self.actionStart.setEnabled(idle)
        self.stopButton.setEnabled(self.running)
        self.actionStop.setEnabled(self.running)
        self.actionSettings.setEnabled(idle)
        self.settingsButton.setEnabled(idle)
        self.sourceBox.setEnabled(idle)
        self.menuSources.setEnabled(idle)

        for action in self.sourceActions.actions():
            action.setEnabled(idle)

        # таблица только после завершения
        table = self.finished and idle
        self.openTableButton.setEnabled(table)
        self.openTableButton.setVisible(table)
        self.actionSave.setEnabled(table)
        self.actionOpen.setEnabled(table)
        self.archiveButton.setEnabled(idle)

    # запуск (парсинг идет прямо тут)
    def start(self):
        if self.running:
            return

        if self.table_dialog is not None:
            self.table_dialog.close()

        code, fetch, normalize = sources[self.sourceBox.currentIndex()]
        self.source_code = code
        self.rows = []
        self.running = True
        self.finished = False
        self.job = parser.Logger(self.append_log, QApplication.processEvents)
        self.update_controls()
        self.statusbar.showMessage("Выполнение · Источник: " + self.sourceBox.currentText())
        self.append_log("Запуск: " + self.sourceBox.currentText())

        try:
            rows = normalize(fetch(self.job))

        except parser.Stopped:
            self.running = False
            self.update_controls()
            self.append_log("Выполнение остановлено пользователем.")
            self.statusbar.showMessage("Выполнение остановлено")
            return

        except Exception as e:
            self.running = False
            self.update_controls()
            self.append_log(f"Ошибка: {e}")
            self.statusbar.showMessage("Ошибка · Источник: " + self.sourceBox.currentText())
            return

        self.running = False
        self.rows = rows
        self.finished = len(rows) > 0

        try:
            save_run(self.source_code, self.rows)
        except Exception as e:
            self.append_log(f"Ошибка базы: {e}")

        self.draw_map(self.rows, self.fuels)

        self.update_controls()

        if len(rows) > 0:
            self.append_log(f"Найдено АЗС: {len(rows)}. Выполнение завершено.")
            self.statusbar.showMessage("Выполнение завершено · Источник: " + self.sourceBox.currentText())

        else:
            self.append_log("АЗС не найдены.")
            self.statusbar.showMessage("Нет данных · Источник: " + self.sourceBox.currentText())

    # стоп
    def stop(self):
        if not self.running:
            return

        self.job.stop()
        self.stopButton.setEnabled(False)
        self.actionStop.setEnabled(False)
        self.append_log("Останавливаю…")

    # перерисовывает карту с кружками статусов по выбранному источнику
    def draw_map(self, rows, selected_fuels=None):
        input_path = paths.resource_dir() / "src" / "map" / "map_clean.png"
        output_path = paths.writable_dir() / "src" / "map" / "map_out.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        drawn, total = map_painter.generate_map(
            input_path=str(input_path),
            output_path=str(output_path),
            stations_data=rows,
            selected_fuels=selected_fuels,
        )

        self.map_pixmap = QtGui.QPixmap(str(output_path))
        self.resize_map()
        self.append_log(f"Карта перерисована: {drawn} из {total} точек.")

    # сохраняет таблицу (формат и папка из настроек)
    def export_current(self):
        if self.running:
            return

        if len(self.rows) == 0:
            return

        folder = Path(self.directory).expanduser()
        stamp = datetime.now().strftime("%d.%m.%Y_%H-%M-%S")
        path = folder / f"{stamp}_{self.source_code}_oil_status.{self.file_format.lower()}"
        header = table_header(self.fuels)
        body = table_rows(self.rows, self.fuels)

        try:
            folder.mkdir(parents=True, exist_ok=True)

            if self.file_format == "XLSX":
                write_xlsx(path, header, body)

            else:
                write_csv(path, header, body)

        except Exception as e:
            self.append_log(f"Ошибка экспорта: {e}")
            QtWidgets.QMessageBox.warning(self, "Экспорт", f"Не удалось сохранить файл:\n{e}")
            return

        self.append_log(f"Сохранено: {path}")
        self.statusbar.showMessage("Сохранено · " + path.name)

    # архив отчётов
    def open_archive(self):
        if self.running:
            return

        dialog = ArchiveDialog(self)

        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        run_id = dialog.selected_id

        if run_id is None:
            return

        rows = load_rows(run_id)

        if len(rows) == 0:
            return

        source = None

        for run in list_runs():
            if run["id"] == run_id:
                source = run["source"]
                break

        if source is None:
            return

        if source == "gis2":  # портянка для эстетики
            source = "2gis"

        self.source_code = source
        self.rows = rows
        self.finished = True
        self.running = False
        self.update_controls()
        self.draw_map(rows, self.fuels)

        self.statusbar.showMessage(f"Таблица {self.source_code} открыта")

        # сразу показываем таблицу загруженного архива
        self.open_table()

    # окно с таблицей
    def open_table(self):
        if not self.finished or self.running:
            return

        # окно при первом разе
        if self.table_dialog is None:
            self.table_dialog = QtWidgets.QDialog(self)
            self.table_dialog.resize(980, 420)
            layout = QtWidgets.QVBoxLayout(self.table_dialog)
            table = QtWidgets.QTableWidget(0, 0, self.table_dialog)
            table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            layout.addWidget(table)

            buttons = QtWidgets.QHBoxLayout()
            buttons.addStretch(1)
            export_button = QtWidgets.QPushButton("Сохранить", self.table_dialog)
            export_button.setFixedHeight(32)
            export_button.clicked.connect(self.export_current)
            buttons.addWidget(export_button)
            layout.addLayout(buttons)

        # заголовки, данные и показ
        table = self.table_dialog.findChild(QtWidgets.QTableWidget)
        header_labels = table_header(self.fuels)
        body = table_rows(self.rows, self.fuels)
        center = QtCore.Qt.AlignmentFlag.AlignCenter

        # цвета ячеек наличия топлива
        cell_colors = {
            "Есть": QtGui.QColor("#C6EFCE"),
            "Нет": QtGui.QColor("#FFC7CE"),
            "Возможно": QtGui.QColor("#FFEB9C"),
            "Н/Д": QtGui.QColor("#D9D9D9"),
        }

        table.setColumnCount(len(header_labels))
        table.setHorizontalHeaderLabels(header_labels)
        table.setRowCount(len(body))

        for r in range(len(body)):
            for c in range(len(body[r])):
                item = QtWidgets.QTableWidgetItem(body[r][c])

                if c >= 2:
                    item.setTextAlignment(center)
                    color = cell_colors.get(body[r][c])
                    if color is not None:
                        item.setBackground(color)
                        # В тёмной теме шрифт в цветных ячейках — тёмный
                        if self.theme == "dark":
                            item.setForeground(QtGui.QColor("#000000"))

                table.setItem(r, c, item)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # виды топлива — одинаковой фиксированной ширины, чтобы не прятались за адресом
        for c in range(2, len(header_labels)):
            header.setSectionResizeMode(c, QHeaderView.ResizeMode.Fixed)
            header.resizeSection(c, 70)

        # название берём по источнику самой таблицы (для архива он может отличаться от выбранного в списке)
        title = self.sourceBox.currentText()
        for i, (code, _, _) in enumerate(sources):
            if code == self.source_code:
                title = self.sourceBox.itemText(i)
                break
        self.table_dialog.setWindowTitle("Таблица · " + title)
        self.table_dialog.show()
        self.table_dialog.raise_()
        self.table_dialog.activateWindow()
        self.append_log(f"Таблица {self.source_code} открыта.")

    # включает и выключает полный экран
    def set_full_screen(self, enabled):
        if enabled:
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.showFullScreen()

        else:
            self.showNormal()
            self.setFixedSize(self.window_size_for_menubar())

    # фиксирует размер окна (чтобы не двигать)
    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            self.actionFullScreen.setChecked(self.isFullScreen())
            if hasattr(self, "initial_size"):
                if self.isFullScreen():
                    self.setMinimumSize(0, 0)
                    self.setMaximumSize(16777215, 16777215)

                elif self.isMaximized():
                    QtCore.QTimer.singleShot(0, self.showNormal)

                else:
                    self.setFixedSize(self.window_size_for_menubar())

    # останавливает парсинг при закрытии окна
    def closeEvent(self, event):
        if self.running:
            self.job.stop()

        super().closeEvent(event)

    # о программе
    def show_about(self):
        box = QtWidgets.QMessageBox(self)
        box.setWindowTitle("О программе")
        box.setIcon(QtWidgets.QMessageBox.Icon.NoIcon)
        box.setTextFormat(QtCore.Qt.TextFormat.RichText)
        box.setText(
            f"<h3>Наличие топлива в Канаше</h3>"
            f"<p>Версия {APP_VERSION}</p>"
            "<p>Программа собирает наличие бензина, дизеля и газа на АЗС Канаша "
            "из трёх источников (2ГИС, Т-Банк, Сбер АЗС), показывает его таблицей "
            "и на карте и сохраняет отчёты в CSV или XLSX. Все запуски попадают в архив, "
            "их можно открыть позже.</p>"
            "<p><b>Важно:</b> Данные могут быть неполными или устаревшими, а формат ответа может измениться. "
            "Перед поездкой лучше проверить наличие на самой АЗС.</p>"
            "<p>Карта: © OpenStreetMap.<br>")
        box.exec()

    # справка
    def show_help(self):
        box = QtWidgets.QMessageBox(self)
        box.setWindowTitle("Как пользоваться")
        box.setIcon(QtWidgets.QMessageBox.Icon.NoIcon)
        box.setTextFormat(QtCore.Qt.TextFormat.RichText)
        box.setText(
            "<h3>Как пользоваться</h3>"
            "<ol>"
            "<li><b>Источник.</b> Выберите в списке 2GIS, T-Bank или SBER "
            "(или в меню «Парсинг → Источники»).</li>"
            "<li><b>Старт.</b> Нажмите «Старт»: ход работы виден в журнале, "
            "«Стоп» останавливает запрос. После завершения карта обновится сама.</li>"
            "<li><b>Таблица.</b> «Открыть таблицу» показывает все найденные АЗС. "
            "Статусы: «Есть», «Возможно», «Нет», «Н/Д» (нет данных).</li>"
            "<li><b>Отчёт.</b> «Экспорт» в окне таблицы или «Файл → Сохранить» "
            "записывает файл CSV или XLSX в папку результатов.</li>"
            "<li><b>Настройки.</b> Здесь выбираются виды топлива (от 1 до 5), "
            "папка результатов, формат файла и тема.</li>"
            "<li><b>Архив.</b> «Архив отчётов…» хранит все прошлые запуски. "
            "Выберите запуск и нажмите «Открыть»: карта и таблица загрузятся сразу. "
            "«Удалить» убирает запуск из архива.</li>"
            "</ol>"
            "<h4>Как читать карту</h4>"
            "<p>У каждой АЗС есть кружок и плашка с названием и наличием выбранных видов топлива. "
            "Цвет кружка считается по тем же видам топлива, что показаны в плашке. "
            "Если видов несколько, приоритет такой: зелёный (есть) выше жёлтого "
            "(возможно есть), затем красный (нет), затем серый (нет данных).</p>"
            "<p>АЗС, которых нет в выбранном источнике, остаются серыми.</p>"
            "<h4>Если что-то не работает</h4>"
            "<p>Отключите VPN: с ним запросы могут не проходить. "
            "Если источник не отвечает, попробуйте другой или повторите позже.</p>"
            "<p>Под Windows строка меню скрыта: нажмите и отпустите <b>Alt</b>, "
            "чтобы показать её, <b>Esc</b> убирает обратно.</p>")
        box.exec()


# старт
if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_fonts(app)

    # иконка окна (положи свою картинку в src/assets/icon.png)
    icon_path = paths.resource_dir() / "src" / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QtGui.QIcon(str(icon_path)))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())