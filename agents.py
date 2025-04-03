from typing import List, Dict
from dataclasses import dataclass
from enum import Enum
import math

from filters import TransmissionModel, bayesian_update

CONTACT_NETWORK_PROXIMITY_THRESHOLD = 10


@dataclass
class LocationRecord:
    x: float
    y: float


class HumanSelfReport(Enum):
    HEALTHY = 0
    SICK = 1


@dataclass
class HumanContactRecord:
    other_id: int
    other_status: HumanSelfReport  # other person's status at time of contact
    duration: int
    average_proximity: float


class Human:
    id: int
    location: LocationRecord
    status: HumanSelfReport = HumanSelfReport.HEALTHY
    transmission_model: TransmissionModel = TransmissionModel()

    location_history: Dict[int, LocationRecord] = {}  # time -> location
    contact_network: Dict[int, HumanContactRecord] = {}  # time -> contact
    self_reports: Dict[int, HumanSelfReport] = {}  # time -> report

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
        for human in sim.human_agents:
            if human.id == self.id:
                continue

            dx = self.location.x - human.location.x
            dy = self.location.y - human.location.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist <= CONTACT_NETWORK_PROXIMITY_THRESHOLD:
                print(f"Human {self.id} contacted other human {human.id}")

                if sim.time_step - 1 in self.contact_network:
                    # we were already in contact with this person
                    record = self.contact_network[sim.time_step - 1]
                    total_proximity = record.average_proximity * record.duration
                    record.duration += 1
                    record.average_proximity += (
                        total_proximity + dist
                    ) / record.duration

                    self.contact_network[sim.time_step - 1] = record
                else:
                    # otherwise create a new contact record
                    record = HumanContactRecord(
                        other_id=human.id,
                        other_status=human.status,
                        duration=1,
                        average_proximity=dist,
                    )
                    self.contact_network[sim.time_step] = record

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
