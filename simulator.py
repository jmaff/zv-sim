import random
from itertools import chain

import pygame

from agents import *


GRID_WIDTH = 600
GRID_HEIGHT = 600

SIM_TICK_TIME_SECONDS = 10
FRAMES_PER_SECOND = 30
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
            print(f"Total animal hazard: {h.hazard_experienced}")
            print(f"Contact network: {h.contact_network}")
            print(f"Sickness records: {h.sickness_records}")
            print("")


class Renderer:
    def __init__(self, simulation, width, height):
        pygame.init()
        self.simulation = simulation
        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Agent Movement Simulation")
        self.clock = pygame.time.Clock()

        self.bg_color = (255, 255, 255)

    def render(self):
        self.screen.fill(self.bg_color)

        for agent in self.simulation.animal_agents:
            screen_x = int(agent.location.x)
            screen_y = int(agent.location.y)

            color = (0, 200, 0)  # green for animals
            radius = agent.radius

            pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)

        for agent in self.simulation.human_agents.values():
            screen_x = int(agent.location.x)
            screen_y = int(agent.location.y)

            color = (0, 0, 255)  # Blue for humans
            radius = 5

            pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)

        pygame.display.flip()
        self.clock.tick(FRAMES_PER_SECOND)


def convert_path(input):
    path = {}
    for p in input:
        path[seconds_to_sim_ticks(p[0])] = LocationRecord(x=p[1], y=p[2])
    return path


HUMAN_PATH_1 = [
    (0, 100, 100),
    (200, 500, 100),
    (400, 500, 500),
    (600, 100, 500),
]  # contacts animal

HUMAN_PATH_2 = [
    (0, 100, 100),
    (200, 150, 100),
    (400, 500, 500),
    (600, 100, 500),
]  # does not contact animal

OTHER_HUMAN_PATH = [
    (0, 200, 100),
    (200, 160, 100),
    (400, 490, 500),
    (600, 300, 500),
]  # contacts other human, does not contact animal


def main():
    print("**ECE 598 VIRUS SIMULATOR**")
    print(f"1 sim second = {REAL_SECONDS_PER_SIM_SECOND} real world seconds")

    sim = Simulation()

    reports = {seconds_to_sim_ticks(410): HumanSelfReport.SICK}
    reports2 = {seconds_to_sim_ticks(500): HumanSelfReport.SICK}
    path1 = convert_path(HUMAN_PATH_1)

    human_agent = Human(id=0, location_history=path1, reports=reports)
    sim.add_agent(human_agent)

    path2 = convert_path(OTHER_HUMAN_PATH)
    other_human_agent = Human(id=1, location_history=path2, reports=reports2)
    sim.add_agent(other_human_agent)

    animal_agent = AnimalPresence(
        id=0,
        migration_pattern={0: LocationRecord(x=450, y=150)},
        radius=100,
        hazard_rate=0.1,
    )
    sim.add_agent(animal_agent)

    renderer = Renderer(simulation=sim, width=GRID_WIDTH, height=GRID_HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        sim.update()
        renderer.render()

        if sim.time_step > seconds_to_sim_ticks(STOP_SIM_AFTER):
            running = False

    sim.print_results()

    pygame.quit()


if __name__ == "__main__":
    main()
