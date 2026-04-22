import numpy as np
import sys

# Allow passing filepath as command line argument or hardcode one
filepath = sys.argv[1] if len(sys.argv) > 1 else "test_run.npz"

data = np.load(filepath, allow_pickle=True)

print("=== NPZ FILE INSPECTOR ===")
print(f"File: {filepath}")
print(f"Keys: {data.files}")
print()

trajectory = list(data["data"])
print(f"Total steps recorded: {len(trajectory)}")
print()

if trajectory:
    print("=== FIRST STEP ===")
    first_step = trajectory[0].item() if hasattr(trajectory[0], "item") else trajectory[0]
    for key, value in first_step.items():
        print(f"  {key}: {type(value).__name__} → {value if not hasattr(value, 'keys') else list(value.keys())}")
    print()

    print("=== AGENT 0 DETAIL (FIRST STEP) ===")
    first_step = trajectory[0].item() if hasattr(trajectory[0], "item") else trajectory[0]
    print(f"  obs: {first_step['obs']['agent_0']}")
    print(f"  action: {first_step['actions']['agent_0']}")
    print(f"  reward: {first_step['reward']['agent_0']}")
    print(f"  term: {first_step['term']['agent_0']}")
    print(f"  trunc: {first_step['trunc']['agent_0']}")

    print("=== AGENT 0 DETAIL (LAST STEP) ===")
    first_step = trajectory[-1].item() if hasattr(trajectory[-1], "item") else trajectory[-1]
    print(f"  obs: {first_step['obs']['agent_0']}")
    print(f"  action: {first_step['actions']['agent_0']}")
    print(f"  reward: {first_step['reward']['agent_0']}")
    print(f"  term: {first_step['term']['agent_0']}")
    print(f"  trunc: {first_step['trunc']['agent_0']}")

    print("=== LAST STEP ===")
    last_step = trajectory[-1].item() if hasattr(trajectory[-1], "item") else trajectory[-1]
    for key, value in last_step.items():
        print(f"  {key}: {type(value).__name__} → {value if not hasattr(value, 'keys') else list(value.keys())}")