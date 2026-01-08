from subprocess import run as run_subprocess

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QCursor, QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from rapidfuzz import fuzz, process

from .items import *


class MainWindow(QWidget):
    def __init__(self, config, groups, input_field):
        super().__init__()
        self.CONFIG = config
        self.supported_events = {
            "fuzzy search": self.fuzzy_finding,
            "calculator": None,
            "open": None,
            "command": None,
        }

        self.selected_index = 0
        self.old_labels = []

        for group in groups:
            self.all_entries = group.entries
        self.window_setup()
        self.input_field = self.create_text_input(input_field)

        self.entry_labels_dict = {}

        for entry_name in self.all_entries:
            self.entry_labels_dict[str(entry_name)] = self.create_text_label(
                str(entry_name)
            )

        self.entry_labels_list = list(self.entry_labels_dict.values())

        self.refresh_labels(
            self.entry_labels_list,
            [self.selected_index, self.CONFIG.ENTRIES_VISIBLE_ENTRIES],
        )

        self.central_widget.show()

    def window_setup(self):
        # ----------------------------
        # Window setup
        # ----------------------------
        # Remove window decoration
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        # Dimensions of window
        self.setGeometry(
            self.CONFIG.WINDOW_X,
            self.CONFIG.WINDOW_Y,
            self.CONFIG.WINDOW_WIDTH,
            self.CONFIG.WINDOW_HEIGHT,
        )

        # Create a central widget to hold the layout
        self.central_widget = QWidget(self)
        self.central_widget.setGeometry(self.rect())
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(
            self.CONFIG.WINDOW_MARGIN_LEFT,
            self.CONFIG.WINDOW_MARGIN_TOP,
            self.CONFIG.WINDOW_MARGIN_RIGHT,
            self.CONFIG.WINDOW_MARGIN_BOTTOM,
        )
        # Center the window on the active screen
        self.center_on_screen()

    def center_on_screen(self):
        # Get screen under the cursor, fallback to primary screen
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Top-center position (like Spotlight)
        x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
        y = (
            screen_geometry.y() + self.CONFIG.WINDOW_TOP_OFFSET
        )  # offset from top menu bar
        self.move(x, y)

    def create_text_input(self, input_field):
        """
        creates search field/text input field
        only one possible (yet)
        """

        text_input_field = QLineEdit(self)
        text_input_field.setPlaceholderText(input_field.display_text)

        # key event
        text_input_field.installEventFilter(self)

        action = input_field.action
        event = self.supported_events[action]
        if event == "command":
            text_input_field.textChanged.connect(
                lambda text: self.execute_command(text, input_field.command)
            )
        else:
            text_input_field.textChanged.connect(event)

        self.main_layout.addWidget(text_input_field)
        return text_input_field

    def create_text_label(self, text: str):
        label = QLabel(text)
        label.setMinimumSize(200, 40)
        label.setMaximumSize(200, 40)
        label.setProperty("selected", False)
        label.setVisible(False)
        return label

    def refresh_labels(self, labels, visible_range):
        for label in self.old_labels:
            print(label.text())
            label.setVisible(False)
            self.main_layout.removeWidget(label)
        self.old_labels = []
        for i, label in enumerate(labels):
            if visible_range[0] <= i < visible_range[1]:
                self.main_layout.addWidget(label)
                label.setVisible(True)
                label.setProperty("selected", i == self.selected_index)
                label.style().unpolish(label)
                label.style().polish(label)
                self.old_labels.append(label)

    def move_selection(self, delta: int, labels: list[QLabel]):
        new_index = max(0, min(self.selected_index + delta, len(labels) - 1))

        if new_index == self.selected_index:
            return

        self.selected_index = new_index

        self.refresh_labels(
            labels,
            [
                min(len(labels) - self.CONFIG.ENTRIES_VISIBLE_ENTRIES, new_index),
                new_index + self.CONFIG.ENTRIES_VISIBLE_ENTRIES,
            ],
        )

    # ----------------------------
    # Fuzzy search logic
    # ----------------------------
    def fuzzy_finding(self, text):
        """
        Updates self.entries based on a combination of:
        - Prefix matches (exact start of entry names)
        - Fuzzy matches via RapidFuzz (partial_ratio)
        """

        # Perform prefix match
        prefix_matches = [
            name
            for name in self.all_entries.keys()
            if name.lower().startswith(text.lower())
        ]

        # Entries not included in prefix match
        rest = [name for name in self.all_entries.keys() if name not in prefix_matches]

        # Return top 20 fuzzy matches
        fuzzy_matches = process.extract(
            text, rest, scorer=fuzz.partial_ratio, limit=self.CONFIG.FUZZY_LIMIT
        )

        final = prefix_matches + [r[0] for r in fuzzy_matches]
        self.selected_index = -1
        self.entry_labels_list = [self.entry_labels_dict[name] for name in final]
        self.move_selection(self.CONFIG.ENTRIES_DELTA, self.entry_labels_list)

    def execute_command(self, text, command):
        cmd = command.format(input=text)
        return run_subprocess(cmd, shell=True, capture_output=True, text=True)

    # ----------------------------
    # Keyboard handling
    # ----------------------------
    def eventFilter(self, source, event):
        """
        Intercepts key events for the text input:
        - Up/Down: navigate selection
        - Enter: execute command
        - Escape: close window
        """
        if isinstance(source, QLineEdit) and event.type() == QEvent.Type.KeyPress:
            # if source is self.input_field and event.type() == QEvent.Type.KeyPress:
            # Down key -> move selection down
            if event.key() == Qt.Key.Key_Down:
                self.move_selection(self.CONFIG.ENTRIES_DELTA, self.entry_labels_list)
                return True

            # Up key -> move selection up
            if event.key() == Qt.Key.Key_Up:
                self.move_selection(-self.CONFIG.ENTRIES_DELTA, self.entry_labels_list)
                return True

            # Return and enter key -> execute command and closes app
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                name = self.entry_labels_list[self.selected_index]
                self.all_entries[str(name.text())].execute_command()
                self.close()
                return True

            # Esc key -> close app
            if event.key() == Qt.Key.Key_Escape:
                self.close()
                return True

        return super().eventFilter(source, event)
