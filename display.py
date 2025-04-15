import pygame

from agents import HumanStatus

FRAMES_PER_SECOND = 30


class Display:
    def __init__(self, simulation, width, height):
        pygame.init()
        self.simulation = simulation
        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Agent Movement Simulation")
        self.clock = pygame.time.Clock()

        self.bg_color = (255, 255, 255)

    # Returns whether the simulation should continue running
    def render(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

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

            if agent.status == HumanStatus.SICK:
                color = (255, 0, 0)  # sick human = red
            else:
                color = (0, 0, 255)  # healthy human = blue

            radius = 5

            pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)

        pygame.display.flip()
        self.clock.tick(FRAMES_PER_SECOND)

        return True

    def cleanup(self):
        pygame.quit()
