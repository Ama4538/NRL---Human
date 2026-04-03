import numpy as np
import time
import datetime
import os
from pyquaticus import pyquaticus_v0
from pyquaticus.config import config_dict_std 
from pyquaticus.base_policies.key_agent import KeyAgent

class AgentController:
    def __init__(self, agent_type: str, controller, agent_id, label: str = ""):
        self.agent_type = agent_type #"keyboard", "heuristic", "rl"
        self.controller = controller
        self.agent_id = agent_id
        self.label = label #policy name or path

    def get_action(self, obs, info):
        if self.agent_type == "keyboard":
            return self.controller.compute_action(obs[self.agent_id], info)
        elif self.agent_type == "heuristic": 
            agent_obs = {self.agent_id : info[self.agent_id]['unnorm_obs']}
            return self.controller.compute_action(agent_obs)
        elif self.agent_type == "rl":
            return self.controller.compute_single_action(obs[self.agent_id])[0]
        raise ValueError(f"Unknown agent type: {self.agent_type}")

        

class PyquaticusWrapper:
    def __init__(self, agent_map, team_size = 3, render_mode="human"):
        self.agent_map = agent_map
        self.team_size = team_size
        self.render_mode = render_mode

        self.env = None
        self.trajectory = [] #List of dictionaries that contain information from each step
        #self.key_agent = None

    def get_action(self, agent_id, obs, info):
        curr_agent = self.agent_map.get(agent_id)
        if curr_agent is None: 
            return 0
        return curr_agent.get_action(obs, info)

    def launch_env(self):
        config = config_dict_std.copy()
        
        config['sim_speedup_factor'] = 2
        
        self.env = pyquaticus_v0.PyQuaticusEnv(
            config_dict = config,
            render_mode = self.render_mode,
            team_size = self.team_size,
        )

        from pyquaticus.base_policies.deprecated.base_attack import BaseAttacker
        from pyquaticus.base_policies.deprecated.base_defend import BaseDefender
        from pyquaticus.base_policies.deprecated.base_combined import Heuristic_CTF_Agent
        from pyquaticus.structs import Team

        policy_map = {
                "Base Attack": BaseAttacker,
                "Base Defend": BaseDefender,
                "Base Combined": Heuristic_CTF_Agent
        }

        for agent_id, entry in self.agent_map.items():
            if entry is not None and entry.agent_type == "heuristic":
                agent_idx = int(agent_id.split("_")[1])
                team = Team.BLUE_TEAM if agent_idx < self.team_size else Team.RED_TEAM
                policy_class = policy_map[entry.label]
                entry.controller = policy_class(
                    agent_id = agent_id, 
                    team = team,
                    max_speed = self.env.max_speeds[agent_idx],
                    aquaticus_field_points=self.env.aquaticus_field_points, 
                )

    def run(self, max_steps = 500): #setting 100 for testing, 500 for normal runs, can be adjusted as needed
        obs, info = self.env.reset()

        for step in range(max_steps):
            
            actions = {}

            for agent_id in obs.keys():
                actions[agent_id] = self.get_action(
                    agent_id,
                    obs,
                    info
                )


            next_obs, reward, term, trunc, info = self.env.step(actions)

            self.trajectory.append({
                "obs": obs,
                "actions": actions,
                "reward": reward, 
                "term": term,
                "trunc": trunc,
                "info": info,
            })

            obs = next_obs

            if any(term.values()) or any(trunc.values()):
                break

            #time.sleep(frame_delay)

        self.env.close()

    #Saves trajectory to npz file
    def save(self, filename = "test_run", tag = "NoTag"):
        folder = os.path.join(os.path.dirname(__file__), "../data/sessions")
        os.makedirs(folder, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(folder, f"{filename}_{tag}_{timestamp}.npz")

        np.savez_compressed(save_path, data=self.trajectory)
        print(f"Saved gameplay data to {save_path}")
        return save_path