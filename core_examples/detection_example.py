from SwarmSwIM import Simulator
from SwarmSwIM import Plotter
from SwarmSwIM import Agent
from SwarmSwIM import CNNDetection
import matplotlib.pyplot as plt

# import os
# DIR_FILE = os.path.dirname(__file__)

# initiate simulator at 24 fps
S = Simulator(1/24, sim_xml="my_sim.xml")
# S = Simulator(1/24, sim_xml=os.path.join(DIR_FILE,"my_sim.xml"))

# add additional agents
AgentB = Agent('B01',initialPosition=(4.0, 0., 0.), initialHeading=180.0, agent_xml="my_agent.xml")
S.add(AgentB)

# adding optinal graphics
circle = plt.Circle((0, 0), 20, color='g', fill=False, alpha=0.5)
# initiate animator class
Animation = Plotter(S,artistics=[circle])

Detection = CNNDetection()

def animation_callback():
    """Move the simulation foward 1 step."""
    S.tick()  # advance 1 time step
    output = Detection(S) # execute detection
    print (output)

# MAIN
Animation.update_plot(callback=animation_callback)

# print(AgentB.NNDetector)