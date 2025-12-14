from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QCursor, QMouseEvent
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QVBoxLayout, QWidget
from rapidfuzz import fuzz, process

from .entries import Entry


class SelectableLabelApp(QWidget):
    """
    Main widget for a searchable, selectable list of entries.
    Features:
    - Text input for searching entries
    - Label list for displaying and selecting entries
    - Keyboard navigation and selection
    - Fuzzy search integration via RapidFuzz
    - Styling is handled via an external QSS file.
    """

    def __init__(self, entries: list[Entry], input_field, CONFIG):
        super().__init__()
        self.CONFIG = CONFIG

        # ----------------------------
        # Data initialization
        # ----------------------------
        # Original list of entries
        self.entries = entries
        # Map name -> entry
        self.name_to_entry = {entry.name: entry for entry in self.entries}
        # Current selected entry
        self.current_index = self.CONFIG.ENTRIES_START_INDEX
        # Start index of visible labels
        self.window_start = self.CONFIG.ENTRIES_WINDOW_START
        # QLable widget for displaying entries
        self.labels = []

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
        self.setLayout(self.main_layout)
        # Center the window on the active screen
        self.center_on_screen()

        # ----------------------------
        # UI setup
        # ----------------------------
        self.input_field = input_field
        self.setup_text_input()  # Input field
        self.setup_labels()  # Lable list for entries

        # Show the parent widget
        self.central_widget.show()

    # ----------------------------
    # Window spawn
    # ----------------------------
    def center_on_screen(self):
        """
        Move the window to the active screen where the mouse cursor currently is.

        If the cursor is not on any screen, the window will default to the primary screen.
        The window is positioned near the top-center of the screen, with a small vertical
        offset to mimic the typical macOS Spotlight position.
        """

        # Get screen under the cursor, fallback to primary screen
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Top-center position (like Spotlight)
        x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
        y = (
            screen_geometry.y() + self.CONFIG.WINDOW_TOP_OFFSET
        )  # offset from top menu bar
        self.move(x, y)

    # ----------------------------
    # Text input setup
    # ----------------------------
    def setup_text_input(self):
        """
        Creates the input box and connects signals.
        """
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText(self.input_field.display_text)
        # Intercept key event
        self.text_input.installEventFilter(self)
        # Update results as user types
        self.text_input.textChanged.connect(self.on_text_changed)
        self.main_layout.addWidget(self.text_input)

    # ----------------------------
    # Label setup
    # ----------------------------
    def setup_labels(self):
        """
        Creates VISIBLE_COUNT QLabel widgets.
        Each label displays an entry name and highlights when selected.
        """
        for _ in range(self.CONFIG.ENTRIES_VISIBLE_ENTRIES):
            label = QLabel("")
            # For QSS highlighting
            label.setProperty("selected", False)
            self.labels.append(label)
            self.main_layout.addWidget(label)
            # Initialize labels
            self.refresh_labels()

    # ----------------------------
    # Refresh labels based on entries
    # ----------------------------
    def refresh_labels(self):
        """
        Updates the visible labels according to:
        - Current window start (scrolling)
        - Selected index
        - Whether the entry exists
        """
        for i, label in enumerate(self.labels):
            entry_index = self.window_start + i

            if entry_index < len(self.entries):
                label.setText(self.entries[entry_index].name)
                label.setVisible(True)

                selected = entry_index == self.current_index
                label.setProperty("selected", selected)
            else:
                label.setVisible(False)
                label.setProperty("selected", False)

            # Force style update
            label.style().unpolish(label)
            label.style().polish(label)

    # ----------------------------
    # Selection logic
    # ----------------------------
    def move_selection(self, delta):
        """
        Moves the selection up/down by delta.
        Adjusts window_start to keep selection visible.
        """
        new_index = max(0, min(self.current_index + delta, len(self.entries) - 1))

        if new_index == self.current_index:
            return

        self.current_index = new_index

        # Scroll window if selection moves out of visible range
        if self.current_index < self.window_start:
            self.window_start = self.current_index
        elif (
            self.current_index
            >= self.window_start + self.CONFIG.ENTRIES_VISIBLE_ENTRIES
        ):
            self.window_start = (
                self.current_index - self.CONFIG.ENTRIES_VISIBLE_ENTRIES + 1
            )

        self.refresh_labels()

    # ----------------------------
    # Input field handeling
    # ----------------------------
    def on_text_changed(self, text):
        """Triggered whenever text input changes."""
        if self.input_field.command == "BUILD_IN_fuzzy":
            self.fuzzy_finding(text)
        else:
            print("FIX IT")

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
            for name in self.name_to_entry.keys()
            if name.lower().startswith(text.lower())
        ]

        # Entries not included in prefix match
        rest = [
            name for name in self.name_to_entry.keys() if name not in prefix_matches
        ]

        # Return top 20 fuzzy matches
        fuzzy_matches = process.extract(
            text, rest, scorer=fuzz.partial_ratio, limit=self.CONFIG.FUZZY_LIMIT
        )

        final = prefix_matches + [r[0] for r in fuzzy_matches]
        self.current_index = -1
        self.entries = [self.name_to_entry[name] for name in final]
        self.move_selection(self.CONFIG.ENTRIES_DELTA)

    # ----------------------------
    # Mouse handling
    # ----------------------------
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None

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
        if source is self.text_input and event.type() == QEvent.Type.KeyPress:
            # Down key -> move selection down
            if event.key() == Qt.Key.Key_Down:
                self.move_selection(self.CONFIG.ENTRIES_DELTA)
                return True

            # Up key -> move selection up
            if event.key() == Qt.Key.Key_Up:
                self.move_selection(-self.CONFIG.ENTRIES_DELTA)
                return True

            # Return and enter key -> execute command and closes app
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.entries[self.current_index].execute_command()
                self.close()
                return True

            # Esc key -> close app
            if event.key() == Qt.Key.Key_Escape:
                self.close()
                return True

        return super().eventFilter(source, event)
