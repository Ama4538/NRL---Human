import sys
import csv
import os
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QPushButton, QCheckBox, QScrollArea, QLineEdit, QSizePolicy, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

try:
    from data_collection.validation import split_valid_invalid_rows
except ModuleNotFoundError:
    from validation import split_valid_invalid_rows

PRIMARY_COLOR = "#263065"
SECONDARY_COLOR = "#c4c7dc"
ACCENT_COLOR = "#44508B"
SECONDARY_SHADE_ONE = "#dddfeb"
SECONDARY_SHADE_TWO = "#eaebf3"
TINT_COLOR = "#5A5A5A"
TEXT_COLOR = "#1C1C1C"
ALT_TEXT_COLOR = "#FFFFFF"

LARGE_FONT_SIZE = "30px"
MED_FONT_SIZE = "20px"
DEFAULT_FONT_SIZE = "16px"
SMALL_FONT_SIZE = "14px"

SPACING = 20

class Data_Dashboard(QMainWindow):
    def __init__(self, entries=None):
        super().__init__()
        # If no entries passed, use a small stub list so UI isn't empty in demo
        if entries is None:
            self._entries = [
                ["Game_1", "30:20", "D&C"],     # valid
                ["", "30:20", "tag"],           # invalid: missing name
                ["Game_3", "bad_time", "tag"],  # invalid: bad time
            ]
        else:
            self._entries = list(entries)
        self._valid, self._invalid = split_valid_invalid_rows(self._entries)
        self.setWindowTitle("Data Collection Dashboard")
        self.setMinimumSize(450, 720)
        self.resize(500, 800)
        
        # Main container
        container = QScrollArea()
        container.setWidgetResizable(True)
        container.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        container.setStyleSheet("border: none;")

        content = QWidget()
        content.setStyleSheet(f"background: {ALT_TEXT_COLOR};")
        container.setWidget(content)
        self.setCentralWidget(container)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(35, 20, 35, 20)

        # Content
        title = QLabel("Data Collection Dashboard")
        title.setStyleSheet(f"font-size: {LARGE_FONT_SIZE}; font-weight: 700; color: {PRIMARY_COLOR}")
        layout.addWidget(title, alignment = Qt.AlignTop)
        layout.addSpacing(SPACING)
        
        # Stats Cards
        total_collected_card = self.create_stat_card("Total Collected Data", len(self._valid), "Games", store_key="_total_label")
        invalid_collected_card = self.create_stat_card("Total Invalid Data", len(self._invalid), "Invalid", store_key="_invalid_label")
        layout_h_card = QHBoxLayout()
        layout_h_card.setSpacing(10)
        layout_h_card.addWidget(total_collected_card)
        layout_h_card.addWidget(invalid_collected_card)
        layout.addLayout(layout_h_card)

        # Valid collected data
        layout.addSpacing(SPACING)
        layout_v_collected = QVBoxLayout()
        self._layout_v_collected = layout_v_collected
        layout_v_collected.setSpacing(10)
        layout_h_collected_title = QHBoxLayout()
        layout_h_collected_buttons = QHBoxLayout()

        collected_title = self.create_section_title("Recently Collected")

        # TODO: ADD function to export selected
        collected_export = self.create_button("Export", self.on_export_valid_clicked)
        collected_delete = self.create_button("Delete", None)

        layout_h_collected_buttons.addWidget(collected_delete)
        layout_h_collected_buttons.addWidget(collected_export)

        layout_h_collected_title.addWidget(collected_title)
        layout_h_collected_title.addStretch()
        layout_h_collected_title.addLayout(layout_h_collected_buttons)
        
        # Collected Data Table
        collected_table_header = self.create_table_row(["Name", "Time", "Tag", "Selected"])
        self._collected_table_content, self._valid_checkboxes = self.create_table_content(self._valid)

        layout_v_collected.addLayout(layout_h_collected_title)
        layout_v_collected.addWidget(collected_table_header)
        layout_v_collected.addWidget(self._collected_table_content)
        layout.addLayout(layout_v_collected)

        # Invalid data
        layout.addSpacing(SPACING)
        layout_v_invalid = QVBoxLayout()
        self._layout_v_invalid = layout_v_invalid
        layout_v_invalid.setSpacing(10)
        layout_h_invalid_title = QHBoxLayout()
        layout_h_invalid_buttons = QHBoxLayout()

        invalid_title = self.create_section_title("Invalid Data")    

        # TODO: ADD function to export selected
        invalid_export = self.create_button("Export", self.on_export_invalid_clicked)
        invalid_delete = self.create_button("Keep", None)

        layout_h_invalid_buttons.addWidget(invalid_delete)
        layout_h_invalid_buttons.addWidget(invalid_export)

        layout_h_invalid_title.addWidget(invalid_title)
        layout_h_invalid_title.addStretch()
        layout_h_invalid_title.addLayout(layout_h_invalid_buttons)
        
        # invalid Data Table
        invalid_table_header = self.create_table_row(["Name", "Time", "Error", "Selected"])
        self._invalid_table_content, self._invalid_checkboxes = self.create_table_content(self._invalid)

        layout_v_invalid.addLayout(layout_h_invalid_title)
        layout_v_invalid.addWidget(invalid_table_header)
        layout_v_invalid.addWidget(self._invalid_table_content)
        layout.addLayout(layout_v_invalid)

        # Settings
        layout.addSpacing(SPACING)
        layout_h_settings_tag = QHBoxLayout()
        layout_h_settings_recording = QHBoxLayout()
        layout_v_settings = QVBoxLayout()
        layout_v_settings.setSpacing(10)

        setting_title = self.create_section_title("Settings")
        
        tag = QLabel("Gameplay Tag")
        tag.setStyleSheet(f"font-size: {DEFAULT_FONT_SIZE}; font-weight: 600; color {TEXT_COLOR}")
        tag_input = QLineEdit()
        tag_input.setPlaceholderText("Enter Tag Name")
        tag_input.setStyleSheet(f"background: {ALT_TEXT_COLOR}; border-radius: 4px; color: {TEXT_COLOR}; border: 1px solid {TINT_COLOR}; font-size: {DEFAULT_FONT_SIZE}; padding: 0px 5px 0px 5px")
        tag_input.setFixedHeight(40)
        layout_h_settings_tag.addWidget(tag, stretch=1)
        layout_h_settings_tag.addWidget(tag_input, stretch=1)

        recording = QLabel("Recording Status")
        recording.setStyleSheet(f"font-size: {DEFAULT_FONT_SIZE}; font-weight: 600; color {TEXT_COLOR}")

        # TODO: Add option to toggle on and off
        recording_button = self.create_button("Recording", None, 100, 40, DEFAULT_FONT_SIZE)
        layout_h_settings_recording.addWidget(recording)
        layout_h_settings_recording.addWidget(recording_button)

        layout_v_settings.addWidget(setting_title)
        layout_v_settings.addLayout(layout_h_settings_tag)
        layout_v_settings.addLayout(layout_h_settings_recording)
        layout.addLayout(layout_v_settings)

        # Start Game Button
        layout.addSpacing(SPACING)
        start_button = self.create_button("Start Game", None, 200, 50, MED_FONT_SIZE)
        start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(start_button, stretch = 1)

        layout.addStretch()

    # Function to create stat card
    def create_stat_card(self, title, value, data_type, store_key=None):
        card = QFrame()
        card.setStyleSheet(f"background: {PRIMARY_COLOR}; border-radius: 4px; color: {ALT_TEXT_COLOR};")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        # Labels
        title = QLabel(title)
        title.setStyleSheet(f"font-size: {DEFAULT_FONT_SIZE};")

        value = QLabel(f"{value} {data_type}")
        value.setStyleSheet(f"font-size: {LARGE_FONT_SIZE}; font-weight: 500")

        if store_key:
            setattr(self, store_key, value)

        layout.addWidget(title)
        layout.addWidget(value)
        return card

    # Create section title
    def create_section_title(self, title):
        title = QLabel(title)
        title.setStyleSheet(f"font-size: {MED_FONT_SIZE}; font-weight: 700; color: {PRIMARY_COLOR}")
        return title

    # Create a table header layout
    def create_table_row(self, labels, selectable=False, checkbox=None):
        header = QFrame()
        header.setStyleSheet(f"background-color: {SECONDARY_COLOR}; border-radius: 4px; font-weight: 600")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(5, (15 if selectable else 10), 5, (15 if selectable else 10))

        for i, text in enumerate(labels):
            container = QWidget()
            column_layout = QHBoxLayout(container)
            column_layout.setContentsMargins(0, 0, 0, 0)

            # Add check box to the last element if allowed
            if (i == len(labels) - 1 and selectable):
                cb = checkbox if checkbox is not None else QCheckBox()
                cb.setCursor(QCursor(Qt.PointingHandCursor))
                column_layout.setContentsMargins(0, 0, 30, 0)
                column_layout.addWidget(cb, alignment=Qt.AlignRight | Qt.AlignVCenter)
            else:
                label = QLabel(text)
                label.setStyleSheet(f"font-size: {SMALL_FONT_SIZE}px; color: {TEXT_COLOR};")

                # Change the aligment for both ends
                if i == 0:
                    label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    label.setStyleSheet(f"font-size: {SMALL_FONT_SIZE}; color: {TEXT_COLOR}; padding-left: 10px;")
                elif i == len(labels) - 1:
                    label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    label.setStyleSheet(f"font-size: {SMALL_FONT_SIZE}; color: {TEXT_COLOR}; padding-right: 10px;")
                else:
                    label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    label.setStyleSheet(f"font-size: {SMALL_FONT_SIZE}; color: {TEXT_COLOR};")

                column_layout.addWidget(label)
        
            layout.addWidget(container, stretch = 1)


        return header
    
    # Create table content — returns (container, checkboxes)
    def create_table_content(self, content):
        container = QScrollArea()
        container.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        container.setWidgetResizable(True)
        container.setStyleSheet("border: none;")
        container.setMinimumHeight(175)
        table = QWidget()

        container.setWidget(table)
        layout = QVBoxLayout(table)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        checkboxes = []
        for i, (name, time, tag) in enumerate(content):
            cb = QCheckBox()
            checkboxes.append(cb)
            row = self.create_table_row([name, time, tag, ""], True, checkbox=cb)
            layout.addWidget(row)

            if i % 2 == 0:
                row.setStyleSheet(f"background-color: {SECONDARY_SHADE_ONE}; border-radius: 4px; font-weight: 600")
            else:
                row.setStyleSheet(f"background-color: {SECONDARY_SHADE_TWO}; border-radius: 4px; font-weight: 600")

        layout.addStretch()
        return container, checkboxes


    # Generate Default button
    def create_button(self, title, on_click, width = 100, height = 25, textSize = SMALL_FONT_SIZE):
        button = QPushButton(title)
        button.setMinimumWidth(width)
        button.setFixedHeight(height)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet(f"background: {ACCENT_COLOR}; border-radius: 4px; color: {ALT_TEXT_COLOR}; font-size: {textSize}; font-weight: 500;")
        if on_click is not None:
            button.clicked.connect(on_click)
        return button


    def _refresh_tables(self):
        self._valid, self._invalid = split_valid_invalid_rows(self._entries)
        self._total_label.setText(f"{len(self._valid)} Games")
        self._invalid_label.setText(f"{len(self._invalid)} Invalid")
        self._collected_table_content.setParent(None)
        self._invalid_table_content.setParent(None)
        self._collected_table_content, self._valid_checkboxes = self.create_table_content(self._valid)
        self._invalid_table_content, self._invalid_checkboxes = self.create_table_content(self._invalid)
        self._layout_v_collected.addWidget(self._collected_table_content)
        self._layout_v_invalid.addWidget(self._invalid_table_content)

    def _write_csv(self, path, rows):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    def on_export_valid_clicked(self):
        selected = [row for row, cb in zip(self._valid, self._valid_checkboxes) if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Export", "No rows selected.\nCheck the boxes next to the rows you want to export.")
            return
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"valid_data_{timestamp}.csv"
        export_path = os.path.join(os.path.dirname(__file__), "exports", filename)
        self._write_csv(export_path, [["name", "time", "tag"]] + selected)
        os.system(f'open "{os.path.dirname(export_path)}"')
        QMessageBox.information(self, "Export", f"Exported {len(selected)} valid game(s) to:\nexports/{filename}")

    def on_export_invalid_clicked(self):
        selected = [row for row, cb in zip(self._invalid, self._invalid_checkboxes) if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Export", "No rows selected.\nCheck the boxes next to the rows you want to export.")
            return
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"invalid_data_{timestamp}.csv"
        quarantine_path = os.path.join(os.path.dirname(__file__), "exports", filename)
        self._write_csv(quarantine_path, [["name", "time", "error"]] + selected)
        os.system(f'open "{os.path.dirname(quarantine_path)}"')
        QMessageBox.information(self, "Export", f"Exported {len(selected)} invalid row(s) to:\nexports/{filename}")

    def get_colleceted_data(self):
        return self._valid

    def get_invalid_data(self):
        return self._invalid

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Data_Dashboard()
    window.show()
    sys.exit(app.exec())