from SwarmSwIM import Simulator
from SwarmSwIM import Plotter
from SwarmSwIM import Agent
from SwarmSwIM import AcousticChannel
import matplotlib.pyplot as plt

TIME_STEP = 1 / 24
# initiate simulator at 24 fps
S = Simulator(TIME_STEP, sim_xml="my_sim.xml")

# add additional agents
AgentB = Agent('B01',initialPosition=(750.0, 0., 0.), agent_xml="my_agent.xml")
AgentC = Agent('C01',initialPosition=(-750.0, 0., 0.), agent_xml="my_agent.xml")
S.add(AgentB, AgentC)

# adding optinal graphics
circle = plt.Circle((0, 0), 20, color='g', fill=False, alpha=0.5)
# initiate animator class
Animation = Plotter(S,artistics=[circle])

# initiate acoustic channel
Channel = AcousticChannel()
# send message
call_response = Channel.send(AgentB, S, duration=1.0, payload="Hello from B01")
print(f"\n Sending 1st msg result: {call_response} at {S.time:.2f} s")

TIME_2ND_MSG = 0.5
# TIME_2ND_MSG = 1.5
# TIME_2ND_MSG = 3

def animation_callback():
    """Move the simulation foward 1 step."""
    S.tick()  # advance 1 time step
    events = Channel(S) # spin acoustic channel
    # if anything happen print
    if events:
        print(f"time: {S.time}: {events}")
    # send second msg
    if S.time > TIME_2ND_MSG and S.time - TIME_STEP <= TIME_2ND_MSG:
        call_response = Channel.send(AgentC, S, duration=1.0, payload="Hello from C01")
        print(f"\n Sending 2st msg result: {call_response} at {S.time:.2f} s")

# MAIN
Animation.update_plot(callback=animation_callback)