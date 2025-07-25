import numpy as np
from ...sail_extension.wind_plotter import WindPlotter
from ...sail_extension.physics import WindField
from ...sail_extension.sail_agent import SailAgent
from SwarmSwIM import Simulator


# TODO: REMOVE AND REPLACE WITH SIM WHEN SAIL FORCES WORKING
class TestSim:
    def __init__(self, agents, dt=0.1, wind_field=WindField()):
        self.agents = agents
        self.Dt = dt
        self.time = 0.0
        self.wind_field = wind_field

    def tick(self):
        for agent in self.agents:
            wind_vec = self.wind_field.get_wind_at_position(agent.pos, self.time)

            agent_turn_rate = 10.0

            # Agent circle path
            agent.psi += agent_turn_rate * self.Dt
            if agent.psi > 360:
                agent.psi -= 360

            agent.calculate_speed(wind_vec)

        self.time += self.Dt


if __name__ == "__main__":
    agents = [
        SailAgent(
            "A",
            initialPosition=np.array([-15.0, 0.0, 0.0]),
            initialHeading=0.0,
        ),
        SailAgent(
            "B",
            initialPosition=np.array([-10.0, 5.0, 0.0]),
            initialHeading=90.0,
        ),
        SailAgent(
            "C",
            initialPosition=np.array([-5.0, -10.0, 0.0]),
            initialHeading=180.0,
        ),
    ]

    wind_field = WindField(
        base_wind_speed=3, base_wind_direction=45.0, turbulence_intensity=0.5
    )

    sim = TestSim(agents, wind_field=wind_field)
    # sim = Simulator(
    #     1 / 24,
    #     sim_xml="sail_extension/simulation.xml",
    # )

    plotter = WindPlotter(
        simulator=sim, wind_field=wind_field, SIZE=25, show_wind=True, wind_grid_size=4
    )

    def simulation_callback():
        sim.tick()

    plotter.update_plot(callback=simulation_callback)
