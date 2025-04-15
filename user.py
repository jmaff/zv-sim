from dataclasses import dataclass
from typing import List
import math
import random

from agents import HumanStatus
from probability import *


# Called if there's no location data for this timestep
def human_motion(human, current_time):
    next_time, next_location = next(
        (
            (t, loc)
            for t, loc in sorted(human.location_history.items())
            if t > current_time
        ),
        (None, None),
    )

    # DO NOTHING
    # pass

    # RANDOM WALK
    # human.location.x += random.randint(-5, 5)
    # human.location.y += random.randint(-5, 5)

    # WEIGHTED RANDOM WALK (to next known location)
    # if next_location is None:
    #     return

    # WEIGHTED_RANDOM_WALK_BIAS_STRENGTH = 0.5

    # dx = next_location.x - human.location.x
    # dy = next_location.y - human.location.y
    # dist = math.hypot(dx, dy)

    # if dist == 0:
    #     direction = (0, 0)
    # else:
    #     direction = (dx / dist, dy / dist)

    # angle_noise = random.uniform(-math.pi, math.pi)
    # noise_dx = math.cos(angle_noise)
    # noise_dy = math.sin(angle_noise)

    # dx = (
    #     WEIGHTED_RANDOM_WALK_BIAS_STRENGTH * direction[0]
    #     + (1 - WEIGHTED_RANDOM_WALK_BIAS_STRENGTH) * noise_dx
    # )
    # dy = (
    #     WEIGHTED_RANDOM_WALK_BIAS_STRENGTH * direction[1]
    #     + (1 - WEIGHTED_RANDOM_WALK_BIAS_STRENGTH) * noise_dy
    # )

    # norm = math.hypot(dx, dy)
    # dx = (dx / norm) * 5.0
    # dy = (dy / norm) * 5.0

    # human.location.x += dx * 5.0
    # human.location.y += dy * 5.0

    # NOISY LINEAR INTERPOLATION
    if next_location is None:
        return

    dx = next_location.x - human.location.x
    dy = next_location.y - human.location.y
    dt = next_time - current_time

    max_noise = 8

    human.location.x += dx / dt + random.randint(-max_noise, max_noise)
    human.location.y += dy / dt + random.randint(-max_noise, max_noise)


# Called if there's no location data for this timestep
def animal_motion(animal):
    # DO NOTHING
    pass

    # RANDOM WALK
    # animal.location.x += random.randint(-5, 5)
    # animal.location.y += random.randint(-5, 5)
    # animal.radius += random.randint(-5, 5)


# P(zoonotic) model for a sick human
def zoonotic_probability_model(sickness_record) -> float:
    hazard_experienced = sickness_record.start_infection_model.experienced_animal_hazard
    secondary_cases = sickness_record.secondary_cases

    return bayesian_p_zoonotic(
        hazard_experienced=hazard_experienced, secondary_cases=secondary_cases
    )


@dataclass
class InfectionModel:
    output_hazard: float
    experienced_animal_hazard: float
    experienced_human_hazard: float

    def total_experienced_hazard(self) -> float:
        return self.experienced_animal_hazard + self.experienced_human_hazard

    def __str__(self):
        return f"(output_hazard={self.output_hazard}, exp_animal_hazard={self.experienced_animal_hazard}, exp_human_hazard={self.experienced_human_hazard})"


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
