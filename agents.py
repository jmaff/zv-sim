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
    start_time: int
    total_proximity: float
    end_time: int = None

    def duration(self):
        return self.end_time - self.start_time

    def average_proximity(self):
        return self.total_proximity / self.duration()


@dataclass
class HumanSicknessRecord:
    p_animal_transmission: float
    start_time: int
    end_time: int = None


@dataclass
class Human:
    def __init__(
        self,
        id: int,
        location_history: Dict[int, LocationRecord],
        reports: Dict[int, HumanSelfReport],
    ):
        self.id: int = id
        self.location_history: Dict[int, LocationRecord] = (
            location_history  # time -> location
        )
        self.self_reports: Dict[int, HumanSelfReport] = reports  # time -> report

        self.location: LocationRecord = None
        self.status: HumanSelfReport = HumanSelfReport.HEALTHY
        self.prev_status: HumanSelfReport = HumanSelfReport.HEALTHY
        self.transmission_model: TransmissionModel = TransmissionModel()

        self.contact_network: Dict[int, HumanContactRecord] = {}  # time -> contact
        self.sickness_records: List[HumanSicknessRecord] = []
        self.active_contacts: Dict[int, HumanContactRecord] = {}  # other id -> contact

    def move(self, sim):
        if sim.time_step in self.location_history:
            self.location = self.location_history[sim.time_step]
        else:
            # random walk? nothing?
            pass

        if sim.time_step in self.self_reports:
            self.status = self.self_reports[sim.time_step]

    def update(self, sim):
        # check if previous contacts are sick, update filter

        # check if in animal radius, update filter
        for animal in sim.animal_agents:
            dx = self.location.x - animal.location.x
            dy = self.location.y - animal.location.y

            dist = math.sqrt(dx**2 + dy**2)
            if dist <= animal.radius:
                self.transmission_model.add_hazard(animal.hazard_rate)

        # check if in contact with a person, update network + filter
        for human in sim.human_agents:
            if human.id == self.id:
                continue

            dx = self.location.x - human.location.x
            dy = self.location.y - human.location.y
            dist = math.sqrt(dx**2 + dy**2)

            if dist <= CONTACT_NETWORK_PROXIMITY_THRESHOLD:
                if human.id in self.active_contacts:
                    # we were already in contact with this person
                    self.active_contacts[human.id].total_proximity += dist
                    print("existing record")
                else:
                    # otherwise create a new contact record
                    record = HumanContactRecord(
                        other_id=human.id,
                        other_status=human.status,
                        start_time=sim.time_step,
                        total_proximity=dist,
                    )
                    print("new record")
                    self.active_contacts[human.id] = record

            else:
                # check if we went out of conact
                if human.id in self.active_contacts:
                    print("contact ended")
                    record = self.active_contacts[human.id]
                    record.end_time = sim.time_step
                    self.contact_network[record.start_time] = record
                    del self.active_contacts[human.id]
        # calculate probabilities
        if self.status == HumanSelfReport.SICK:
            p = bayesian_update(self.transmission_model.get_p_animal_transmission())

            if self.prev_status == HumanSelfReport.HEALTHY:
                record = HumanSicknessRecord(
                    p_animal_transmission=p, start_time=sim.time_step
                )
                self.sickness_records.append(record)
            else:
                self.sickness_records[-1].p_animal_transmission = p
        elif (
            self.status == HumanSelfReport.HEALTHY
            and self.prev_status == HumanSelfReport.SICK
        ):
            self.sickness_records[-1].end_time = sim.time_step

        self.prev_status = self.status


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
