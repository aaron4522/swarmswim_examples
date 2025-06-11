from SwarmSwIM import Simulator
from SwarmSwIM import Plotter
from SwarmSwIM import Agent
import matplotlib.pyplot as plt


# initiate simulator at 24 fps
S = Simulator(1/24, sim_xml="my_sim.xml")

# add additional agents
AgentB = Agent('B01',initialPosition=(4.0, 0., 0.), initialHeading=90.0, agent_xml="my_agent.xml")
S.add(AgentB)
# add command
# AgentB.cmd_yawrate = 15.0
# AgentB.cmd_planar = (10.0, 0)
# AgentB.cmd_local_vel = 1.0

for agent in S.agents:
    agent.cmd_forces = 1.5
    agent.cmd_heading = 0

# adding optinal graphics
circle = plt.Circle((0, 0), 20, color='g', fill=False, alpha=0.5)
# initiate animator class
Animation = Plotter(S,artistics=[circle])

def animation_callback():
    """Move the simulation foward 1 step."""
    S.tick()  # advance 1 time step

# MAIN
Animation.update_plot(callback=animation_callback)