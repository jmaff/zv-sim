from dataclasses import dataclass
import math

P_SICK_GIVEN_NO_ANIMAL_TRANSMISSION = 0.01
P_SICK_GIVEN_ANIMAL_TRANSMISSION = 1.0


@dataclass
class TransmissionModel:
    hazard_experienced: float = 0  # per sim tick (TODO: change to per real time?)

    def add_hazard(self, hazard_rate: float, duration: int = 1):
        self.hazard_experienced += hazard_rate * duration

    def get_p_animal_transmission(self):
        return 1 - math.exp(-self.hazard_experienced)


def bayesian_update(p_animal_transmission: float):
    return (
        p_animal_transmission
        * P_SICK_GIVEN_ANIMAL_TRANSMISSION
        / (
            p_animal_transmission * P_SICK_GIVEN_ANIMAL_TRANSMISSION
            + (1 - p_animal_transmission) * P_SICK_GIVEN_NO_ANIMAL_TRANSMISSION
        )
    )
