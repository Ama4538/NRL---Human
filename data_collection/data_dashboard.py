import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QPushButton, QCheckBox, QScrollArea, QLineEdit, QSizePolicy, QComboBox, QFileDialog, QMessageBox, QInputDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

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
        
        # Stats Cards
        total_collected_card = self.create_stat_card("Total Collected Data", 0, "Games")
        invalid_collected_card = self.create_stat_card("Total Invalid Data", 0, "Invalid")
        layout_h_card = QHBoxLayout()
        layout_h_card.setSpacing(10)
        layout_h_card.addWidget(total_collected_card)
        layout_h_card.addWidget(invalid_collected_card)
        layout.addLayout(layout_h_card)

        # Valid collected data
        layout.addSpacing(SPACING)
        layout_v_collected = QVBoxLayout()
        layout_v_collected.setSpacing(10)
        layout_h_collected_title = QHBoxLayout()
        layout_h_collected_buttons = QHBoxLayout()

        collected_title = self.create_section_title("Recently Collected")

        # TODO: ADD function to export selected
        collected_export = self.create_button("Export", None)
        collected_delete = self.create_button("Delete", None)

        layout_h_collected_buttons.addWidget(collected_delete)
        layout_h_collected_buttons.addWidget(collected_export)

        layout_h_collected_title.addWidget(collected_title)
        layout_h_collected_title.addStretch()
        layout_h_collected_title.addLayout(layout_h_collected_buttons)
        
        # Collected Data Table 
        collected_table_header = self.create_table_row(["Name", "Time", "Tag", "Selected"])
        collected_table_content = self.create_table_content(self.get_colleceted_data())

        layout_v_collected.addLayout(layout_h_collected_title)
        layout_v_collected.addWidget(collected_table_header)
        layout_v_collected.addWidget(collected_table_content)
        layout.addLayout(layout_v_collected)

        # Invalid data
        layout.addSpacing(SPACING)
        layout_v_invalid = QVBoxLayout()
        layout_v_invalid.setSpacing(10)
        layout_h_invalid_title = QHBoxLayout()
        layout_h_invalid_buttons = QHBoxLayout()

        invalid_title = self.create_section_title("Invalid Data")    

        # TODO: ADD function to export selected
        invalid_export = self.create_button("Export", None)
        invalid_delete = self.create_button("Keep", None)

        layout_h_invalid_buttons.addWidget(invalid_delete)
        layout_h_invalid_buttons.addWidget(invalid_export)

        layout_h_invalid_title.addWidget(invalid_title)
        layout_h_invalid_title.addStretch()
        layout_h_invalid_title.addLayout(layout_h_invalid_buttons)
        
        # invalid Data Table 
        invalid_table_header = self.create_table_row(["Name", "Time", "Error", "Selected"])
        invalid_table_content = self.create_table_content(self.get_invalid_data())

        layout_v_invalid.addLayout(layout_h_invalid_title)
        layout_v_invalid.addWidget(invalid_table_header)
        layout_v_invalid.addWidget(invalid_table_content)
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

        #------------Policy Selection and Loading Section ------------------------------------
        #Creates agent policy dictionary that will be passed into wrapper class to assign agent policies
        self.agent_policies = {
            f"agent_{i}": None for i in range(6) #3v3 agents
        }

        #Main Layout 
        agent_widget = QWidget()
        agent_layout = QVBoxLayout(agent_widget)

        agent_label = QLabel("Agent Policy Selection")
        agent_layout.addWidget(agent_label)

        self.agent_dropdowns = {}
        self.agent_load_buttons = {}

        for i in range(6):
            self.add_agent_row(i, agent_layout)

        layout.addWidget(agent_widget)

        #----------------End Policy Selection and Loading------------


        # Start Game Button
        layout.addSpacing(SPACING)
        start_button = self.create_button("Start Game", None, 200, 50, MED_FONT_SIZE)
        start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        start_button.clicked.connect(self.start_game)
        layout.addWidget(start_button, stretch = 1)

        layout.addStretch()

    # Function to create agent dropdown menus
    def add_agent_row(self, agent_idx, parent_layout): 
        row_layout = QHBoxLayout()
        label = QLabel(f"Agent {agent_idx}:")
        row_layout.addWidget(label)

        dropdown = QComboBox()
        dropdown.addItem("Select Policy")
        dropdown.addItem("Human (Keyboard)")
        dropdown.addItem("Trained Policy")
        dropdown.addItem("Heuristic")
        
        # Ensure dropdown list is opaque and above other widgets
        dropdown.setStyleSheet("""
            QComboBox {
                background-color: white;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #d0d0d0;
            }
        """)

        #Save reference to agent dropdowns
        self.agent_dropdowns[agent_idx] = dropdown

        dropdown.currentIndexChanged.connect(
            lambda _, idx=agent_idx: self.update_load_button(idx)
        )
        
        row_layout.addWidget(dropdown)

        #Load policy button
        load_button = QPushButton("Load Policy")
        load_button.setEnabled(False)

        #Save reference to agent load buttons 
        self.agent_load_buttons[agent_idx] = load_button

        load_button.clicked.connect(lambda _, idx=agent_idx: self.load_policy(idx))
        
        row_layout.addWidget(load_button)

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


    
    def load_policy(self, agent_idx):
        from wrapper.pyquaticus_wrapper import AgentController
        selection = self.agent_dropdowns[agent_idx].currentText()
        agent_key = f"agent_{agent_idx}"

        if selection == "Human (Keyboard)":
            from pyquaticus.base_policies.key_agent import KeyAgent
            self.agent_policies[agent_key] = AgentController("keyboard", KeyAgent(), agent_key) 
            print(f"Agent {agent_idx} assigned to Human (Keyboard).")

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
            print(f"Agent {agent_idx} assigned to Heuristic: {heuristic_type}")


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
            print(f"Agent {agent_idx} policy set to: {policy_dir}")
        
        else:
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid agent policy.")

    def update_load_button(self, agent_idx):
        selection = self.agent_dropdowns[agent_idx].currentText()
        button = self.agent_load_buttons[agent_idx]
        button.setEnabled(selection != "Select Policy")

    def start_game(self):
        from wrapper.pyquaticus_wrapper import PyquaticusWrapper

        if len(self.agent_policies) < 6: 
            QMessageBox.warning(self, "Missing Policies", "Please assign a policy to all agents before starting.")
            return
        
        wrapper = PyquaticusWrapper(agent_map=self.agent_policies, team_size = 3)
        wrapper.launch_env()
        self.close() #TEMPORARY NEED TO REMOVE 
        wrapper.run(max_steps = 300)
        wrapper.save("test_run")


    # Function to create stat card
    def create_stat_card(self, title, value, data_type):
        card = QFrame()
        card.setStyleSheet(f"background: {PRIMARY_COLOR}; border-radius: 4px; color: {ALT_TEXT_COLOR};")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        # Labels
        title = QLabel(title)
        title.setStyleSheet(f"font-size: {DEFAULT_FONT_SIZE};")

        value = QLabel(f"{value} {data_type}")
        value.setStyleSheet(f"font-size: {LARGE_FONT_SIZE}; font-weight: 500")

        layout.addWidget(title)
        layout.addWidget(value)
        return card

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

        for i, text in enumerate(labels):
            container = QWidget()
            column_layout = QHBoxLayout(container)
            column_layout.setContentsMargins(0, 0, 0, 0)

            # Add check box to the last element if allowed
            if (i == len(labels) - 1 and selectable):
                checkbox = QCheckBox()
                checkbox.setCursor(QCursor(Qt.PointingHandCursor))
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

        for i, (name, time, tag) in enumerate(content):
            row = self.create_table_row([name, time, tag, ""], True)
            layout.addWidget(row)

            if i % 2 == 0:
                row.setStyleSheet(f"background-color: {SECONDARY_SHADE_ONE}; border-radius: 4px; font-weight: 600")
            else: 
                row.setStyleSheet(f"background-color: {SECONDARY_SHADE_TWO}; border-radius: 4px; font-weight: 600")
        
        layout.addStretch()
        return container


    # Generate Default button
    def create_button(self, title, on_click, width = 100, height = 25, textSize = SMALL_FONT_SIZE):
        button = QPushButton(title)
        button.setMinimumWidth(width)
        button.setFixedHeight(height)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet(f"background: {ACCENT_COLOR}; border-radius: 4px; color: {ALT_TEXT_COLOR}; font-size: {textSize}; font-weight: 500;")
        # button.clicked.connect(on_click)
        return button


    # TODO: Update method to get data
    def get_colleceted_data(self):
        data = [
        ["Game_1", "30:20", "D&C"],
        ["Game_2", "30:20", "D&C"],
        ["Game_3",  "30:20", "D&C"],
        ["Game_4", "30:20", "D&C"],
        ["Game_5", "30:20", "D&C"],
        ]
        return data
    
    # TODO: Update method to get data
    def get_invalid_data(self):
        data = [
        ["Game_1", "30:20", "Corrupt"],
        ["Game_2", "30:20", "Corrupt"],
        ["Game_3",  "30:20", "Corrupt"],
        ["Game_4", "30:20", "Corrupt"],
        ["Game_5", "30:20", "Corrupt"],
        ]
        return data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Data_Dashboard()
    window.show()
    sys.exit(app.exec())