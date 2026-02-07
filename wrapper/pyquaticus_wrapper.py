import numpy as np
import time
import datetime
import os
from pyquaticus import pyquaticus_v0
from pyquaticus.config import config_dict_std 
from pyquaticus.base_policies.key_agent import KeyAgent

class PyquaticusWrapper:
    def __init__(self, team_size = 3, render_mode="human"):
        self.team_size = team_size
        self.render_mode = render_mode

        self.env = None
        self.trajectory = []
        self.key_agent = None

    def launch_env(self):
        config = config_dict_std.copy()
        
        config['sim_speedup_factor'] = 2
        
        self.env = pyquaticus_v0.PyQuaticusEnv(
            config_dict = config,
            render_mode = self.render_mode,
            team_size = self.team_size,
        )
        self.key_agent = KeyAgent()

    def run(self, max_steps = 500):
        obs, info = self.env.reset()

        for step in range(max_steps):
            actions = {}

            actions['agent_0'] = self.key_agent.compute_action(obs['agent_0'], info)

            for i in range(1, self.team_size * 2):
                actions[f'agent_{i}'] = 0

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

    def save(self, filename = "test_run"):
        folder = os.path.join(os.path.dirname(__file__), "../data/sessions")
        os.makedirs(folder, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(folder, f"{filename}_{timestamp}.npz")

        np.savez_compressed(save_path, data=self.trajectory)
        print(f"Saved gameplay data to {save_path}")