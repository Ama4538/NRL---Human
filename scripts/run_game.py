from wrapper.pyquaticus_wrapper import PyquaticusWrapper

wrapper = PyquaticusWrapper(team_size = 3)
wrapper.launch_env()
wrapper.run(max_steps = 300)
wrapper.save("test_run.npz")

print("Saved gameplay data!")