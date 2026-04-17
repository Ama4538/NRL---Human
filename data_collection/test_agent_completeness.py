import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from wrapper.pyquaticus_wrapper import PyquaticusWrapper


def make_wrapper_with_trajectory(team_size, agent_ids_present):
    """Helper: create a wrapper and inject a fake trajectory with given agent IDs."""
    w = PyquaticusWrapper(agent_map={}, team_size=team_size)
    # Build one step where only the given agents appear in obs
    obs = {agent_id: [0.0] * 4 for agent_id in agent_ids_present}
    w.trajectory = [{"obs": obs, "actions": {}, "reward": {}, "term": {}, "trunc": {}, "info": {}}]
    return w


def test_all_agents_present():
    """All 6 agents present in a 3v3 game — should pass."""
    all_agents = [f"agent_{i}" for i in range(6)]
    w = make_wrapper_with_trajectory(team_size=3, agent_ids_present=all_agents)
    ok, reason = w.validate_agent_completeness()
    assert ok, f"Expected valid but got: {reason}"
    assert reason == ""
    print("PASS: test_all_agents_present")


def test_missing_one_agent():
    """One agent missing — should fail and report the missing agent."""
    agents = [f"agent_{i}" for i in range(6) if i != 3]  # agent_3 missing
    w = make_wrapper_with_trajectory(team_size=3, agent_ids_present=agents)
    ok, reason = w.validate_agent_completeness()
    assert not ok, "Expected invalid but got valid"
    assert "agent_3" in reason, f"Expected agent_3 in reason, got: {reason}"
    assert "MISSING_AGENT_DATA" in reason
    assert "AGENT_COUNT_MISMATCH" in reason
    print(f"PASS: test_missing_one_agent — reason: {reason}")


def test_all_agents_missing():
    """Empty trajectory — all agents missing."""
    w = make_wrapper_with_trajectory(team_size=3, agent_ids_present=[])
    ok, reason = w.validate_agent_completeness()
    assert not ok, "Expected invalid but got valid"
    for i in range(6):
        assert f"agent_{i}" in reason, f"agent_{i} not reported missing"
    print(f"PASS: test_all_agents_missing — reason: {reason}")


def test_empty_trajectory():
    """No steps at all — all agents missing."""
    w = PyquaticusWrapper(agent_map={}, team_size=3)
    w.trajectory = []
    ok, reason = w.validate_agent_completeness()
    assert not ok, "Expected invalid but got valid"
    print(f"PASS: test_empty_trajectory — reason: {reason}")


def test_1v1_all_present():
    """1v1: agents 0 and 1 both present."""
    w = make_wrapper_with_trajectory(team_size=1, agent_ids_present=["agent_0", "agent_1"])
    ok, reason = w.validate_agent_completeness()
    assert ok, f"Expected valid but got: {reason}"
    print("PASS: test_1v1_all_present")


def test_1v1_one_missing():
    """1v1: only agent_0 present, agent_1 missing."""
    w = make_wrapper_with_trajectory(team_size=1, agent_ids_present=["agent_0"])
    ok, reason = w.validate_agent_completeness()
    assert not ok, "Expected invalid but got valid"
    assert "agent_1" in reason
    print(f"PASS: test_1v1_one_missing — reason: {reason}")


def test_agents_spread_across_steps():
    """Each agent appears in a different step — should still be found."""
    w = PyquaticusWrapper(agent_map={}, team_size=3)
    w.trajectory = [
        {"obs": {"agent_0": [], "agent_1": []}, "actions": {}, "reward": {}, "term": {}, "trunc": {}, "info": {}},
        {"obs": {"agent_2": [], "agent_3": []}, "actions": {}, "reward": {}, "term": {}, "trunc": {}, "info": {}},
        {"obs": {"agent_4": [], "agent_5": []}, "actions": {}, "reward": {}, "term": {}, "trunc": {}, "info": {}},
    ]
    ok, reason = w.validate_agent_completeness()
    assert ok, f"Expected valid but got: {reason}"
    print("PASS: test_agents_spread_across_steps")


if __name__ == "__main__":
    test_all_agents_present()
    test_missing_one_agent()
    test_all_agents_missing()
    test_empty_trajectory()
    test_1v1_all_present()
    test_1v1_one_missing()
    test_agents_spread_across_steps()
    print("\nAll tests passed.")
