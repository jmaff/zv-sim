from dataclasses import dataclass
from typing import List
import math
import random

from agents import HumanStatus


# Called if there's no location data for this timestep
def human_motion(human):
    # random walk
    human.location.x += random.randint(-5, 5)
    human.location.y += random.randint(-5, 5)


# Called if there's no location data for this timestep
def animal_motion(animal):
    # do nothing
    pass

    # random walk
    # animal.location.x += random.randint(-5, 5)
    # animal.location.y += random.randint(-5, 5)
    # animal.radius += random.randint(-5, 5)


# P(zoonotic) model for a sick human
def zoonotic_probability_model() -> float:
    pass


@dataclass
class InfectionModel:
    output_hazard: float
    experienced_animal_hazard: float
    experienced_human_hazard: float

    def total_experienced_hazard(self) -> float:
        return self.experienced_animal_hazard + self.experienced_human_hazard


SIMULATE_SPREAD = False  # change to False to only use reported illness

# parameters for basic infection model
HUMAN_HAZARD_HEALTHY = 0.0
HUMAN_HAZARD_SICK = 0.03
HAZARD_DECAY = 0.99


# Probability at current timestep that a given human becomes sick
def infection_probability_model(
    human,
    animal_contacts: List,
    human_contacts: List,
) -> bool:
    # update output hazard
    match human.status:
        case HumanStatus.HEALTHY:
            human.infection_model.output_hazard = HUMAN_HAZARD_HEALTHY
        case HumanStatus.SICK:
            human.infection_model.output_hazard = HUMAN_HAZARD_SICK

    # update experienced hazard
    human.infection_model.experienced_human_hazard *= HAZARD_DECAY
    human.infection_model.experienced_animal_hazard *= HAZARD_DECAY

    for a in animal_contacts:
        human.infection_model.experienced_animal_hazard += (
            a.infection_model.output_hazard
        )

    for h in human_contacts:
        human.infection_model.experienced_human_hazard += (
            h.infection_model.output_hazard
        )

    # simulate based on probability
    if not SIMULATE_SPREAD:
        return False

    p_got_sick = 1 - math.exp(-human.infection_model.total_experienced_hazard())
    got_sick = random.random() < p_got_sick

    return got_sick
