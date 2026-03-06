import numpy as np
import time
import datetime
import os
import zmq
import pygame
from pyquaticus import pyquaticus_v0
from pyquaticus.config import config_dict_std 
from pyquaticus.base_policies.key_agent import KeyAgent

class PyquaticusWrapper:
    def __init__(self, agent_map, team_size = 3, render_mode="human"):
        self.agent_map = agent_map
        self.team_size = team_size
        self.render_mode = render_mode

        self.env = None
        self.trajectory = [] #List of dictionaries that contain information from each step
        #self.key_agent = None

        # Initialize ZMQ for external control
        self.zmq_context = zmq.Context()
        self.pub_socket = self.zmq_context.socket(zmq.PUB)
        self.pub_socket.bind("tcp://*:5555") #PORT 55555 for external control


    def get_action(self, agent_id, obs, info):
        #Access agent map values to get correct action based on agent type
        controller = self.agent_map.get(agent_id)

        if controller is None:
            return 0
        
        #Keyboard agent
        if hasattr(controller, "compute_action"):
            return controller.compute_action(obs, info)
        
        #RL Policy
        if hasattr(controller, "compute_single_action"):
            return controller.compute_single_action(obs)[0]
        
        raise ValueError(f"Unknown controller type for {agent_id}")

    def launch_env(self):
        config = config_dict_std.copy()
        
        config['sim_speedup_factor'] = 2
        
        self.env = pyquaticus_v0.PyQuaticusEnv(
            config_dict = config,
            render_mode = self.render_mode,
            team_size = self.team_size,
        )

    def run(self, max_steps = 500):
        obs, info = self.env.reset()

        for step in range(max_steps):
            actions = {}

            for agent_id in obs.keys():
                actions[agent_id] = self.get_action(
                    agent_id,
                    obs[agent_id],
                    info
                )


            next_obs, reward, term, trunc, info = self.env.step(actions)
            
            self.env.render() # Forces the Mac window to draw the frame
            print(f"Step {step} completed...") # Heartbeat in the terminal

            # --- Data broasting for external control ---
            payload = {
                "step": step,
                "reward": {k: float(v) for k, v in reward.items()},
                "game_active": True
            }
            self.pub_socket.send_json(payload)
            # --------------------------------------------- 

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
                self.pub_socket.send_json({"game_active": False}) #Notify external controller that game has ended
                break

            #time.sleep(frame_delay)

        self.env.close()

    #Saves trajectory to npz file
    def save(self, filename = "test_run"):
        folder = os.path.join(os.path.dirname(__file__), "../data/sessions")
        os.makedirs(folder, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(folder, f"{filename}_{timestamp}.npz")

        np.savez_compressed(save_path, data=self.trajectory)
        print(f"Saved gameplay data to {save_path}")