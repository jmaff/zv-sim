from typing import List, Dict
from dataclasses import dataclass
from enum import Enum
import math

from filters import TransmissionModel, bayesian_update


@dataclass
class LocationRecord:
    x: float
    y: float


@dataclass
class HumanContactRecord:
    human_id: int
    duration: int
    proximity: float
    time: int


class HumanSelfReport(Enum):
    HEALTHY = 0
    SICK = 1


class Human:
    id: int
    location: LocationRecord
    status: HumanSelfReport = HumanSelfReport.HEALTHY
    transmission_model: TransmissionModel = TransmissionModel()

    location_history: Dict[int, LocationRecord] = []  # time -> location
    contact_network: List[HumanContactRecord] = []
    self_reports: Dict[int, HumanSelfReport] = []  # time -> report

    def __init__(
        self,
        id: int,
        location_history: Dict[int, LocationRecord],
        reports: Dict[int, HumanSelfReport],
    ):
        self.id = id
        self.location_history = location_history
        self.self_reports = reports

    def move(self, sim):
        if sim.time_step in self.location_history:
            self.location = self.location_history[sim.time_step]
        else:
            # random walk? nothing?
            pass

        if sim.time_step in self.self_reports:
            print("updating status")
            self.status = self.self_reports[sim.time_step]

    def update(self, sim):
        # check if previous contacts are sick, update filter

        # check if in animal radius, update filter
        for animal in sim.animal_agents:
            dx = self.location.x - animal.location.x
            dy = self.location.y - animal.location.y

            dist = math.sqrt(dx**2 + dy**2)
            if dist <= animal.radius:
                print(f"Human {self.id} contacted animal presence {animal.id}")
                self.transmission_model.add_hazard(animal.hazard_rate)

        # check if in contact with a person, update network + filter
        ...

        # calculate probabilities
        if self.status == HumanSelfReport.SICK:
            p = bayesian_update(self.transmission_model.get_p_animal_transmission())
            print(f"Human {self.id} is sick! P(infected by an animal | sick) = {p}")


class AnimalPresence:
    id: int
    location: LocationRecord
    radius: float

    hazard_rate: float  # per sim tick (TODO: change to per real time unit?)
    migration_pattern: Dict[int, LocationRecord]

    def __init__(
        self, id: int, migration_pattern: Dict[int, LocationRecord], radius, hazard_rate
    ):
        self.id = id
        self.migration_pattern = migration_pattern
        self.radius = radius
        self.hazard_rate = hazard_rate

    def move(self, sim):
        if sim.time_step in self.migration_pattern:
            self.location = self.migration_pattern[sim.time_step]
        else:
            # random walk? nothing?
            pass

    def update(self, sim): ...
