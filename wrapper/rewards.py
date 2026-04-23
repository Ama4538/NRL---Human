import math
import numpy as np 

from pyquaticus.structs import Team
from pyquaticus.utils.utils import *

def caps_and_grabs(
    agent_id: str,
    team: Team,
    agents: list,
    agent_inds_of_team: dict,
    state: dict,
    prev_state: dict,
    env_size: np.ndarray,
    agent_radius: np.ndarray,
    catch_radius: float,
    scrimmage_coords: np.ndarray,
    max_speeds: list,
    tagging_cooldown: float
):
    reward = 0.0
    prev_num_oob = prev_state['agent_oob'][agents.index(agent_id)]
    num_oob = state['agent_oob'][agents.index(agent_id)]
    if num_oob > prev_num_oob:
        reward += -1.0
    #for t in state['grabs']:
    for team_idx, num_grabs in enumerate(state['grabs']):

        prev_num_grabs = prev_state['grabs'][team_idx]
        #num_grabs = state['grabs'][t]
        #print(f"t={t}, prev_grabs={prev_num_grabs}, curr_grabs={num_grabs}, diff={num_grabs - prev_num_grabs}")
        if num_grabs > prev_num_grabs:
            #print(f"Grab detected. agent={agent_id}, agent_team={team}, type={type(team)}, grabbing_team={t}, converted={Team(t)}, match={Team(t) == team}")
            agent_team = Team(team_idx) 
            print(f"Grab detected! agent={agent_id}, agent_team={team}, grabbing_team={agent_team}, match={agent_team == team}")
            reward += 0.25 if agent_team == team else -0.25

    for team_idx, num_caps in enumerate(state['captures']):  
        prev_num_caps = prev_state['captures'][team_idx]
        #num_caps = state['captures'][t]
        if num_caps > prev_num_caps:
            agent_team = Team(team_idx)
            reward += 1.0 if agent_team == team else -1.0

    for team_idx, num_caps in enumerate(state['tags']):  
        prev_num_caps = prev_state['tags'][team_idx]
        if num_caps > prev_num_caps:
            agent_team = Team(team_idx)
            reward += 1.0 if agent_team == team else -1.0

    return reward
