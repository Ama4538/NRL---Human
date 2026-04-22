import sys
import os
import shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QPushButton, QCheckBox, QScrollArea, QLineEdit, QSizePolicy, QComboBox, QFileDialog, QMessageBox, QInputDialog, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

PRIMARY_COLOR = "#263065"
SECONDARY_COLOR = "#c4c7dc"
ACCENT_COLOR = "#44508B"
SECONDARY_SHADE_ONE = "#dddfeb"
SECONDARY_SHADE_TWO = "#eaebf3"
TINT_COLOR = "#dcdcdc"
TEXT_COLOR = "#1C1C1C"
ALT_TEXT_COLOR = "#FFFFFF"

LARGE_FONT_SIZE = "30px"
MED_FONT_SIZE = "20px"
DEFAULT_FONT_SIZE = "16px"
SMALL_FONT_SIZE = "14px"

SPACING = 20
TOTAL_AGENT = 6

class Data_Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
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
         
        valid_data, invalid_data = self.get_data_from_disk()

        # Stats Cards
        total_collected_card, self.total_label = self.create_stat_card("Total Collected Data", len(valid_data), "Games")
        invalid_collected_card, self.invalid_label = self.create_stat_card("Total Invalid Data", len(invalid_data), "Invalid")
        layout_h_card = QHBoxLayout()
        layout_h_card.setSpacing(10)
        layout_h_card.addWidget(total_collected_card)
        layout_h_card.addWidget(invalid_collected_card)
        layout.addLayout(layout_h_card)

        # Valid collected data
        layout.addSpacing(SPACING)
        self.layout_v_collected = QVBoxLayout()
        self.layout_v_collected.setSpacing(10)
        layout_h_collected_title = QHBoxLayout()
        layout_h_collected_buttons = QHBoxLayout()

        collected_title = self.create_section_title("Recently Collected")

        collected_export = self.create_button("Export", self.export_valid)
        collected_delete = self.create_button("Delete", self.delete_valid)
        collected_summary = self.create_button("Summary", self.show_summary)

        layout_h_collected_buttons.addWidget(collected_delete)
        layout_h_collected_buttons.addWidget(collected_export)
        layout_h_collected_buttons.addWidget(collected_summary)

        layout_h_collected_title.addWidget(collected_title)
        layout_h_collected_title.addStretch()
        layout_h_collected_title.addLayout(layout_h_collected_buttons)
        
        # Collected Data Table 
        collected_table_header = self.create_table_row(["Name", "Time", "Tag", "Selected"])
        self.collected_table_content, self.valid_checkboxes = self.create_table_content(valid_data)

        self.layout_v_collected.addLayout(layout_h_collected_title)
        self.layout_v_collected.addWidget(collected_table_header)
        self.layout_v_collected.addWidget(self.collected_table_content)
        layout.addLayout(self.layout_v_collected)

        # Invalid data
        layout.addSpacing(SPACING)
        self.layout_v_invalid = QVBoxLayout()
        self.layout_v_invalid.setSpacing(10)
        layout_h_invalid_title = QHBoxLayout()
        layout_h_invalid_buttons = QHBoxLayout()

        invalid_title = self.create_section_title("Invalid Data")    

        invalid_export = self.create_button("Export", self.export_invalid)
        invalid_delete = self.create_button("Delete", self.delete_invalid)

        layout_h_invalid_buttons.addWidget(invalid_delete)
        layout_h_invalid_buttons.addWidget(invalid_export)

        layout_h_invalid_title.addWidget(invalid_title)
        layout_h_invalid_title.addStretch()
        layout_h_invalid_title.addLayout(layout_h_invalid_buttons)
        
        # invalid Data Table 
        invalid_table_header = self.create_table_row(["Name", "Time", "Error", "Selected"])
        self.invalid_table_content, self.invalid_checkboxes = self.create_table_content(invalid_data)

        self.layout_v_invalid.addLayout(layout_h_invalid_title)
        self.layout_v_invalid.addWidget(invalid_table_header)
        self.layout_v_invalid.addWidget(self.invalid_table_content)
        layout.addLayout(self.layout_v_invalid)

        # Settings
        layout.addSpacing(SPACING)
        layout_h_settings_tag = QHBoxLayout()
        layout_h_settings_recording = QHBoxLayout()
        layout_v_settings = QVBoxLayout()
        layout_v_settings.setSpacing(10)

        setting_title = self.create_section_title("Settings")
        
        tag = QLabel("Gameplay Tag")
        tag.setStyleSheet(f"font-size: {DEFAULT_FONT_SIZE}; font-weight: 600; color {TEXT_COLOR}")
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Enter Tag Name")
        self.tag_input.setStyleSheet(f"background: {ALT_TEXT_COLOR}; border-radius: 4px; color: {TEXT_COLOR}; border: 1px solid {PRIMARY_COLOR}; font-size: {DEFAULT_FONT_SIZE}; padding: 0px 5px 0px 5px")
        self.tag_input.setFixedHeight(40)
        layout_h_settings_tag.addWidget(tag, stretch=1)
        layout_h_settings_tag.addWidget(self.tag_input, stretch=1)

        recording = QLabel("Recording Status")
        recording.setStyleSheet(f"font-size: {DEFAULT_FONT_SIZE}; font-weight: 600; color {TEXT_COLOR}")

        self.is_recording = True
        self.recording_button = self.create_button("Recording: ON", self.toggle_recording, 130, 40, DEFAULT_FONT_SIZE)
        layout_h_settings_recording.addWidget(recording)
        layout_h_settings_recording.addWidget(self.recording_button)

        layout_v_settings.addWidget(setting_title)
        layout_v_settings.addLayout(layout_h_settings_tag)
        layout_v_settings.addLayout(layout_h_settings_recording)
        layout.addLayout(layout_v_settings)
        layout.addSpacing(SPACING / 2)

        #------------Policy Selection and Loading Section ------------------------------------
        # Creates agent policy dictionary that will be passed into wrapper class to assign agent policies
        self.agent_policies = {
            f"agent_{i}": None for i in range(TOTAL_AGENT) 
        }

        # Main Layout 
        agent_widget = QWidget()
        agent_layout = QVBoxLayout(agent_widget)
        agent_layout.setSpacing(10)
        agent_layout.setContentsMargins(0, 0, 0, 0)

        agent_label = QLabel("Agent Policy Selection")
        agent_label.setStyleSheet(f"font-size: {DEFAULT_FONT_SIZE}; font-weight: 600; color: {TEXT_COLOR}")
        agent_layout.addWidget(agent_label)
        agent_layout.addSpacing(10)

        self.agent_dropdowns = {}
        self.agent_load_buttons = {}
        self.agent_status_labels = {}

        agent_layout.setSpacing(8)

        for i in range(TOTAL_AGENT):
            self.add_agent_row(i, agent_layout)

        layout.addWidget(agent_widget)

        #----------------End Policy Selection and Loading------------


        # Start Game Button
        layout.addSpacing(SPACING)
        start_button = self.create_button("Start Game", None, 200, 50, MED_FONT_SIZE)
        start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        start_button.clicked.connect(self.start_game)
        layout.addWidget(start_button, stretch = 1)

        # Replay Session Button
        replay_button = self.create_button("Replay Session", None, 200, 50, MED_FONT_SIZE)
        replay_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        replay_button.clicked.connect(self.replay_session)
        layout.addWidget(replay_button, stretch=1)

        layout.addStretch()

    # Function to create agent dropdown menus
    def add_agent_row(self, agent_idx, parent_layout): 
        row_layout = QHBoxLayout()
        label = QLabel(f"Agent {agent_idx}:")
        label.setStyleSheet(f"font-size: {DEFAULT_FONT_SIZE}; font-weight: 600; color: {TEXT_COLOR}; padding-left: 10px;")
        row_layout.addWidget(label)

        dropdown = QComboBox()
        dropdown.setCursor(Qt.PointingHandCursor)
        dropdown.view().viewport().setCursor(Qt.PointingHandCursor)
        dropdown.addItem("Select Policy")
        dropdown.addItem("Human (Keyboard)")
        dropdown.addItem("Trained Policy")
        dropdown.addItem("Heuristic")
        
        # Ensure dropdown list is opaque and above other widgets
        dropdown.setStyleSheet(f"""
            QComboBox {{
                background: {ALT_TEXT_COLOR};
                color: {TEXT_COLOR};
                border: 1px solid {SECONDARY_COLOR};
                border-radius: 4px;
                padding: 2px 5px;
                min-height: 20px;
                font-size: {DEFAULT_FONT_SIZE};
                font-weight: 600;
            }}
            
            QComboBox[selected="true"] {{
                background: {SECONDARY_SHADE_TWO}; 
            }}

            QComboBox::drop-down {{
                border: 0px;
            }}

            QComboBox QAbstractItemView::item:selected {{
                background-color: {SECONDARY_COLOR};
                color: {TEXT_COLOR};
            }}
        """)

        #Save reference to agent dropdowns
        self.agent_dropdowns[agent_idx] = dropdown

        dropdown.currentIndexChanged.connect(
            lambda _, idx=agent_idx: self.update_load_button(idx, dropdown)
        )
        
        row_layout.addWidget(dropdown)

        #Load policy button
        load_button = QPushButton("Select First to Load")
        load_button.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_COLOR}; 
                color: {ALT_TEXT_COLOR}; 
                border: 1px solid {PRIMARY_COLOR}; 
                border-radius: 4px; 
                padding: 2px 5px; 
                min-height: 20px;
            }}

            QPushButton:disabled {{
                background: {TINT_COLOR};       
                color: {TEXT_COLOR};          
                border: 1px solid {TEXT_COLOR};
            }}
        """)
        load_button.setCursor(Qt.PointingHandCursor)
        load_button.setEnabled(False)

        #Save reference to agent load buttons 
        self.agent_load_buttons[agent_idx] = load_button

        load_button.clicked.connect(lambda _, idx=agent_idx: self.load_policy(idx, load_button))

        row_layout.addWidget(load_button)
        
        status_label = QLabel("Not Loaded")
        status_label.setStyleSheet(f"font-size: {MED_FONT_SIZE}px; color: {TEXT_COLOR};")
        self.agent_status_labels[agent_idx] = status_label

        row_layout.addWidget(status_label)



        parent_layout.addLayout(row_layout)

    def validate_policy_path(self, policy_path):
        """
        Returns True of the folder is a valid RLlib agent policy, otherwise False
        Shows a popup error message if invalid
        """

        if not policy_path:
            return False
        
        if not os.path.isdir(policy_path):
            QMessageBox.warning(self, "Invalid Policy", f"The selected path is not a folder:\n{policy_path}")
            return False
        
        #Look for required files
        '''
        For Policy.from_checkpoint() to work, the checkpoint directory needs to contain an
        rllib_checkpoint.json file (metadata about checkpoint version and structure) and a 
        policy_state.pkl file (Store actual neural network weights and state)
        '''

        required_files = ["rllib_checkpoint.json", "policy_state.pkl"]
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(policy_path, f))]

        if missing_files:
            QMessageBox.warning(
                self,
                "Invalid Policy", 
                f"The selected folder is missing the following files:\n" + "\n".join(missing_files)
            )
            return False
        
        return True
    
    def load_policy(self, agent_idx, load_button):
        from wrapper.pyquaticus_wrapper import AgentController
        selection = self.agent_dropdowns[agent_idx].currentText()
        agent_key = f"agent_{agent_idx}"

        try:
            load_button.setText("Loaded")
            if selection == "Human (Keyboard)":
                from pyquaticus.base_policies.key_agent import KeyAgent
                self.agent_policies[agent_key] = AgentController("keyboard", KeyAgent(), agent_key) 
                self.agent_status_labels[agent_idx].setText(f"Agent {agent_idx} assigned to Human (Keyboard).")

            elif selection == "Heuristic":
                heuristic_type, ok = QInputDialog.getItem(
                    self, 
                    f"Select Heuristic Type for Agent {agent_idx}", 
                    "Heuristic Type:",
                    ["Base Attack", "Base Defend", "Base Combined"],
                    editable=False 
                )
                if not ok: 
                    return 
                
                '''
                #Map string to actual policy class 
                from pyquaticus.base_policies.deprecated.base_attack import BaseAttacker
                from pyquaticus.base_policies.deprecated.base_defend import BaseDefender
                from pyquaticus.base_policies.deprecated.base_combined import Heuristic_CTF_Agent

                policy_map = {
                    "Base Attack": BaseAttacker,
                    "Base Defend": BaseDefender,
                    "Base Combined": Heuristic_CTF_Agent
                }
                '''
                #controller = policy_map[heuristic_type]()

                self.agent_policies[agent_key] = AgentController("heuristic", None, agent_key, label=heuristic_type)
                self.agent_status_labels[agent_idx].setText(f"Agent {agent_idx} assigned to Heuristic: {heuristic_type}")

            elif selection == "Trained Policy":
            
                #Open file dialog and store path in agent_policies
                policy_dir = QFileDialog.getExistingDirectory(
                    self, 
                    f"Select Policy Folder for Agent {agent_idx}",
                    "",
                )
                if not policy_dir:
                    return
                
                #Convert to absolute path 
                policy_dir = os.path.abspath(policy_dir)

                #Validate selected path
                if not self.validate_policy_path(policy_dir):
                    return
                
                #Load actual RL policy from the checkpoint path
                from ray.rllib.policy.policy import Policy
                policy = Policy.from_checkpoint(policy_dir)
                self.agent_policies[agent_key] = AgentController("rl", policy, agent_key, label = policy_dir)
                checkpoint_name = os.path.basename(policy_dir)
                self.agent_status_labels[agent_idx].setText(f"Agent {agent_idx} policy set to: {checkpoint_name}")
            
            else:
                load_button.setText("Load Policy")
                QMessageBox.warning(self, "Invalid Selection", "Please select a valid agent policy.")
        except Exception as e:
            load_button.setText("Load Policy")
            print(f"Error Loading Agent {agent_idx}")
            print(e)
            import traceback
            traceback.print_exc()


    def update_load_button(self, agent_idx, dropdown):
        selection = self.agent_dropdowns[agent_idx].currentText()
        button = self.agent_load_buttons[agent_idx]

        valid = selection != "Select Policy"
        button.setText("Load Policy" if valid else "Select First to Load")
        button.setEnabled(valid)
        dropdown.setProperty("selected", valid)
        dropdown.style().unpolish(dropdown)
        dropdown.style().polish(dropdown)
        
    def start_game(self):
        from wrapper.pyquaticus_wrapper import PyquaticusWrapper

        if any(policy is None for policy in self.agent_policies.values()):
            QMessageBox.warning(self, "Missing Policies", "Please assign a policy to all agents before starting.")
            return
        
        wrapper = PyquaticusWrapper(agent_map=self.agent_policies, team_size = 3)
        wrapper.launch_env()
        wrapper.run(max_steps = 300)
        
        if self.is_recording:
            tag = self.tag_input.text().strip() or "NoTag"
            wrapper.save("test_run", tag)
            self.refresh_tables()
            QMessageBox.information(self, "Game Finished", "Game run completed and data was saved successfully.")
        else:
            QMessageBox.information(self, "Game Finished", "Game run completed. Recording was disabled, so no data was saved.")

    # Function to create stat card
    def create_stat_card(self, title, value, data_type):
        card = QFrame()
        card.setStyleSheet(f"background: {PRIMARY_COLOR}; border-radius: 4px; color: {ALT_TEXT_COLOR};")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        # Labels
        title = QLabel(title)
        title.setStyleSheet(f"font-size: {DEFAULT_FONT_SIZE};")

        value_label = QLabel(f"{value} {data_type}")
        value_label.setStyleSheet(f"font-size: {LARGE_FONT_SIZE}; font-weight: 500")

        layout.addWidget(title)
        layout.addWidget(value_label)
        return card, value_label

    # Create section title
    def create_section_title(self, title):
        title = QLabel(title)
        title.setStyleSheet(f"font-size: {MED_FONT_SIZE}; font-weight: 700; color: {PRIMARY_COLOR}")
        return title

    # Create a table header layout
    def create_table_row(self, labels, selectable = False):
        header = QFrame()
        header.setStyleSheet(f"background-color: {SECONDARY_COLOR}; border-radius: 4px; font-weight: 600")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(5, (15 if selectable else 10), 5, (15 if selectable else 10))

        checkbox_widget = None
        for i, text in enumerate(labels):
            container = QWidget()
            column_layout = QHBoxLayout(container)
            column_layout.setContentsMargins(0, 0, 0, 0)

            # Add check box to the last element if allowed
            if (i == len(labels) - 1 and selectable):
                checkbox = QCheckBox()
                checkbox_widget = checkbox
                checkbox.setCursor(QCursor(Qt.PointingHandCursor))
                checkbox.setStyleSheet(f"""
                    QCheckBox::indicator {{
                        width: 18px;
                        height: 18px;
                        border: 2px solid {TEXT_COLOR};
                        border-radius: 3px;
                        background: transparent;
                    }}

                    QCheckBox::indicator:checked {{
                        background: {ACCENT_COLOR};
                        border: 2px solid {ACCENT_COLOR};
                    }}
                """)
                column_layout.setContentsMargins(0, 0, 30, 0)
                column_layout.addWidget(checkbox, alignment=Qt.AlignRight | Qt.AlignVCenter)
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

        if selectable:
            return header, checkbox_widget
        return header
    
    # Create table content
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

        checkboxes = {}
        for i, (name, time, tag) in enumerate(content):
            row_result = self.create_table_row([name, time, tag, ""], True)
            if isinstance(row_result, tuple):
                row, checkbox = row_result
                checkboxes[name] = checkbox
                #Enforce single selection for summary info
                checkbox.stateChanged.connect(
                    lambda state, n=name: self.on_checkbox_selected(n)
                )
            else:
                row = row_result
            layout.addWidget(row)

            if i % 2 == 0:
                row.setStyleSheet(f"background-color: {SECONDARY_SHADE_ONE}; border-radius: 4px; font-weight: 600")
            else: 
                row.setStyleSheet(f"background-color: {SECONDARY_SHADE_TWO}; border-radius: 4px; font-weight: 600")
        
        layout.addStretch()
        return container, checkboxes
    
    def on_checkbox_selected(self, selected_name):
        for name, checkbox in self.valid_checkboxes.items():
            if name != selected_name:
                checkbox.setChecked(False)

    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.recording_button.setText("Recording: ON")
            self.recording_button.setStyleSheet(f"background: {ACCENT_COLOR}; border-radius: 4px; color: {ALT_TEXT_COLOR}; font-size: {DEFAULT_FONT_SIZE}; font-weight: 500;")
        else:
            self.recording_button.setText("Recording: OFF")
            self.recording_button.setStyleSheet(f"background: {SECONDARY_COLOR}; border-radius: 4px; color: {TEXT_COLOR}; font-size: {DEFAULT_FONT_SIZE}; font-weight: 500;")


    # Generate Default button
    def create_button(self, title, on_click, width = 100, height = 25, textSize = SMALL_FONT_SIZE):
        button = QPushButton(title)
        button.setMinimumWidth(width)
        button.setFixedHeight(height)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet(f"background: {ACCENT_COLOR}; border-radius: 4px; color: {ALT_TEXT_COLOR}; font-size: {textSize}; font-weight: 500;")
        if on_click:
            button.clicked.connect(on_click)
        return button


    # Update method to get data
    def refresh_tables(self):
        valid_data, invalid_data = self.get_data_from_disk()
        
        self.total_label.setText(f"{len(valid_data)} Games")
        self.invalid_label.setText(f"{len(invalid_data)} Invalid")
        
        self.layout_v_collected.removeWidget(self.collected_table_content)
        self.collected_table_content.deleteLater()
        self.collected_table_content, self.valid_checkboxes = self.create_table_content(valid_data)
        self.layout_v_collected.addWidget(self.collected_table_content)
        
        self.layout_v_invalid.removeWidget(self.invalid_table_content)
        self.invalid_table_content.deleteLater()
        self.invalid_table_content, self.invalid_checkboxes = self.create_table_content(invalid_data)
        self.layout_v_invalid.addWidget(self.invalid_table_content)

    def delete_data(self, checkboxes):
        files_to_delete = [name for name, cb in checkboxes.items() if cb.isChecked()]
        if not files_to_delete:
            QMessageBox.information(self, "No Selection", "Please select at least one item to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete {len(files_to_delete)} items?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            sessions_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sessions"))
            for name in files_to_delete:
                file_path = os.path.join(sessions_dir, name)
                if os.path.exists(file_path):
                    os.remove(file_path)
            self.refresh_tables()

    def export_data(self, checkboxes):
        files_to_export = [name for name, cb in checkboxes.items() if cb.isChecked()]
        if not files_to_export:
            QMessageBox.information(self, "No Selection", "Please select at least one item to export.")
            return

        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return

        sessions_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sessions"))
        for name in files_to_export:
            src_path = os.path.join(sessions_dir, name)
            dst_path = os.path.join(export_dir, name)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
        QMessageBox.information(self, "Export Successful", f"Successfully exported {len(files_to_export)} items.")

    def show_summary(self):
        #Find which file is selected 
        selected_name = None
        for name, checkbox in self.valid_checkboxes.items():
            if checkbox.isChecked():
                selected_name = name
                break
        if not selected_name:
            return
        sessions_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sessions"))
        filepath = os.path.join(sessions_dir, selected_name)

        # Generate summary
        data = np.load(filepath, allow_pickle=True)
        trajectory = list(data["data"])
        total_steps = len(trajectory)

        # Per agent reward totals and reward events
        agent_totals = {}
        reward_events = []
        for step_idx, step in enumerate(trajectory):
            step = step.item() if hasattr(step, "item") else step
            for agent_id, reward in step["reward"].items():
                agent_totals[agent_id] = agent_totals.get(agent_id, 0) + reward
                if reward != 0.0:
                    reward_events.append(f"  Step {step_idx}: {agent_id} received reward {reward}")

        # Check if ended early
        last_step = trajectory[-1].item() if hasattr(trajectory[-1], "item") else trajectory[-1]
        terminated_early = any(last_step["term"].values()) or any(last_step["trunc"].values())
        global_state = last_step["info"]["agent_0"]["global_state"]
        blue_score = global_state["blue_team_score"]
        red_score = global_state["red_team_score"]

        if blue_score > red_score:
            winner = "Blue Team"
        elif red_score > blue_score:
            winner = "Red Team"
        else:
            winner = "Tie"

        #Load agent metadata if available
        agent_metadata = None
        if "agent_metadata" in data:
            agent_metadata = data["agent_metadata"].item()

        # Build summary text
        summary = f"File: {selected_name}\n\n"
        
        summary += "=== RESULTS ===\n"
        
        summary += f"Winner: {winner}\n"
        summary += f"Score: {blue_score} - {red_score}\n"

        summary += f"Total Steps: {total_steps} ({'ended early' if terminated_early else 'full game'})\n\n"

        summary += "=== AGENT CONFIGURATION ===\n"
        if agent_metadata:
            for agent_id, meta in agent_metadata.items():
                team = "Blue" if int(agent_id.split("_")[1]) < 3 else "Red"
                summary += f"  {agent_id} ({team}): {meta['agent_type']} — {meta['label']}\n"
        else:
            summary += "  No agent metadata recorded (older file)\n"
        
        summary += "\n=== AGENT REWARD SUMMARY ===\n"
        for agent_id, total in agent_totals.items():
            summary += f"  {agent_id}: {total:.2f} total reward\n"
        
        summary += "\n=== REWARD EVENTS ===\n"
        if reward_events:
            summary += "\n".join(reward_events)
        else:
            summary += "  No reward events recorded"

        # Show popup
        dialog = QDialog(self)
        dialog.setWindowTitle("Game Summary")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        text = QLabel(summary)
        text.setStyleSheet(f"font-size: {SMALL_FONT_SIZE}px; color: {TEXT_COLOR};")
        text.setWordWrap(True)
        
        close_button = self.create_button("Close", None, 100, 35, MED_FONT_SIZE)
        close_button.clicked.connect(dialog.close)
        
        layout.addWidget(text)
        layout.addWidget(close_button)
        dialog.exec()

    def delete_valid(self):
        self.delete_data(self.valid_checkboxes)

    def export_valid(self):
        self.export_data(self.valid_checkboxes)

    

    def delete_invalid(self):
        self.delete_data(self.invalid_checkboxes)

    def export_invalid(self):
        self.export_data(self.invalid_checkboxes)

    def replay_session(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Session to Replay",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sessions")),
            "NPZ Files (*.npz)"
        )
        if not filepath:
            return
        from wrapper.pyquaticus_wrapper import PyquaticusWrapper
        wrapper = PyquaticusWrapper(agent_map={}, team_size=3)
        #self.close()
        wrapper.replay(filepath)

    def get_data_from_disk(self):
        sessions_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sessions"))
        if not os.path.exists(sessions_dir):
            return [], []
            
        valid_data = []
        invalid_data = []
        
        for f in reversed(sorted(os.listdir(sessions_dir))):
            if f.endswith(".npz"):
                parts = f.replace(".npz", "").split("_")
                name = f
                time_str = "Unknown"
                tag = "None"
                error = "Corrupted"
                
                if len(parts) >= 4:
                    tag = parts[-3]
                    time_str = f"{parts[-2][:4]}-{parts[-2][4:6]}-{parts[-2][6:]} {parts[-1][:2]}:{parts[-1][2:4]}"
                
                file_path = os.path.join(sessions_dir, f)
                is_valid = False
                try:
                    with np.load(file_path, allow_pickle=True) as data:
                        if 'data' in data and len(data['data']) > 0:
                            is_valid = True
                        else:
                            error = "Empty Trajectory"
                except Exception:
                    error = "Load Failed"
                
                if is_valid:
                    valid_data.append([name, time_str, tag])
                else:
                    invalid_data.append([name, time_str, error])
                    
        return valid_data, invalid_data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Data_Dashboard()
    window.show()
    sys.exit(app.exec())