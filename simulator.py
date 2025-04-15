from itertools import chain

from data import *
from agents import *
from display import *


GRID_WIDTH = 600
GRID_HEIGHT = 600

SIM_TICK_TIME_SECONDS = 10
REAL_SECONDS_PER_SIM_SECOND = FRAMES_PER_SECOND * SIM_TICK_TIME_SECONDS

STOP_SIM_AFTER = 700


def seconds_to_sim_ticks(s: float) -> int:
    return int(s / SIM_TICK_TIME_SECONDS)


class Simulation:
    def __init__(self):
        self.human_agents: Dict[Human] = {}  # id -> Human
        self.animal_agents: List[AnimalPresence] = []
        self.time_step = 0

    def add_agent(self, agent):
        if isinstance(agent, Human):
            self.human_agents[agent.id] = agent
        else:
            self.animal_agents.append(agent)

    def update(self):
        for agent in chain(self.human_agents.values(), self.animal_agents):
            agent.move(self)

        for agent in chain(self.human_agents.values(), self.animal_agents):
            agent.update(self)

        self.time_step += 1

    def print_results(self):
        for h in self.human_agents.values():
            print(f"*** HUMAN {h.id} ***")
            print(f"Final infection model: {h.infection_model}\n")
            print(f"Contact network: {h.contact_network}\n")
            print(f"Sickness records: {h.sickness_records}\n")
            print(f"*** END HUMAN {h.id} ***\n")


USE_DISPLAY = True


def main():
    print("**ECE 598 VIRUS SIMULATOR**")
    print(f"1 sim second = {REAL_SECONDS_PER_SIM_SECOND} real world seconds")

    sim = Simulation()

    if USE_DISPLAY:
        display = Display(simulation=sim, width=GRID_WIDTH, height=GRID_HEIGHT)

    for a in chain(D0_HUMANS, D0_ANIMALS):
        sim.add_agent(a)

    running = True
    while running:
        sim.update()

        if USE_DISPLAY:
            running = display.render()

        if sim.time_step > seconds_to_sim_ticks(STOP_SIM_AFTER):
            running = False

    sim.print_results()

    if USE_DISPLAY:
        display.cleanup()


if __name__ == "__main__":
    main()
