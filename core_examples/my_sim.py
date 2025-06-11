from SwarmSwIM import Simulator
TIME_STEP = 1 / 24  # Simulation time step in seconds

# Initialize the simulator with the chosen time step
S = Simulator(TIME_STEP, sim_xml="my_sim.xml")

# Run the simulation until a specific condition is met
for i in range(1000):
    S.tick()         # Progress the simulation by one time step
    # print(S.states)