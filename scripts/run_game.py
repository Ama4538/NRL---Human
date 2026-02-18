from wrapper.pyquaticus_wrapper import PyquaticusWrapper
from pyquaticus.base_policies.key_agent import KeyAgent
from ray.rllib.policy import Policy
import os

def load_latest_policy(policy_folder_name):
    '''
    Given a folder name (relative to the script), finds the latest checkpoint and loads it as an RLlib Policy
    '''
    base_folder = os.path.join(os.path.dirname(__file__), policy_folder_name)
    if not os.path.exists(base_folder):
        raise FileNotFoundError(f"Policy folder not found: {base_folder}")
    
    if "rllib_checkpoint.json" in os.listdir(base_folder):
        checkpoint_path = base_folder
    else:
        candidates = [
            d for d in os.listdir(base_folder)
            if d.startswith("rllib_checkpoint") and 
                os.path.isdir(os.path.join(base_folder, d))
        ]

        if not candidates:
            raise FileNotFoundError(
                f"No rllib_checkpoint found in {base_folder}"
            )
        
        checkpoint_path = os.path.join(base_folder, candidates[0])

    print(f"Loading RLlib policy from {checkpoint_path}")
    return Policy.from_checkpoint(checkpoint_path)

key_agent = KeyAgent()
#policy_1 = Policy.from_checkpoint(os.path.dirname(__file__), "agent-1-policy")
#policy_2 = Policy.from_checkpoint(os.path.dirname(__file__), "agent-2-policy")
policy_1 = load_latest_policy("agent-1-policy")
policy_2 = load_latest_policy("agent-2-policy")
# TODO: replace hardcoded policy paths with GUI-selected paths

agent_map = {
    "agent_0": key_agent,
    "agent_1": policy_1,
    "agent_2": policy_2,
    "agent_3": None,
    "agent_4": None,
    "agent_5": None,
}


wrapper = PyquaticusWrapper(agent_map=agent_map, team_size = 3)
wrapper.launch_env()
wrapper.run(max_steps = 300)
wrapper.save("test_run")

print("Saved gameplay data!")