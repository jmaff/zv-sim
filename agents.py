from typing import List, Dict
from dataclasses import dataclass
from enum import Enum
import math

from filters import bayesian_p_zoonotic
from simulator import seconds_to_sim_ticks

CONTACT_NETWORK_PROXIMITY_THRESHOLD = 10
INCUBATION_SIM_TIME = seconds_to_sim_ticks(300)  # TODO: make much higher


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
    start_time: int
    p_zoonotic: float = 0
    end_time: int = None
    secondary_cases: int = 0


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
        self.hazard_experienced: float = 0.0

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
                self.hazard_experienced += animal.hazard_rate

        # check if in contact with a person, update network + filter
        for human in sim.human_agents.values():
            if human.id == self.id:
                continue

            dx = self.location.x - human.location.x
            dy = self.location.y - human.location.y
            dist = math.sqrt(dx**2 + dy**2)

            if dist <= CONTACT_NETWORK_PROXIMITY_THRESHOLD:
                if human.id in self.active_contacts:
                    # we were already in contact with this person
                    self.active_contacts[human.id].total_proximity += dist
                else:
                    # otherwise create a new contact record
                    record = HumanContactRecord(
                        other_id=human.id,
                        other_status=human.status,
                        start_time=sim.time_step,
                        total_proximity=dist,
                    )
                    self.active_contacts[human.id] = record
            else:
                # check if we went out of conact
                if human.id in self.active_contacts:
                    record = self.active_contacts.pop(human.id)
                    record.end_time = sim.time_step
                    self.contact_network[record.start_time] = record

        # calculate probabilities
        if self.status == HumanSelfReport.SICK:

            if self.prev_status == HumanSelfReport.HEALTHY:
                record = HumanSicknessRecord(
                    start_time=sim.time_step,
                )
                self.sickness_records.append(record)

            secondary_cases = self.secondary_cases(sim)
            p = bayesian_p_zoonotic(self.hazard_experienced, secondary_cases)

            self.sickness_records[-1].p_zoonotic = p
            self.sickness_records[-1].secondary_cases = secondary_cases
        elif (
            self.status == HumanSelfReport.HEALTHY
            and self.prev_status == HumanSelfReport.SICK
        ):
            self.sickness_records[-1].end_time = sim.time_step

        self.prev_status = self.status

    # only counts one case per sick contacted individual
    def secondary_cases(self, sim):
        if len(self.sickness_records) == 0 or self.status != HumanSelfReport.SICK:
            raise ValueError("Tried to calculate secondary cases when not sick!")

        infectious_at = self.sickness_records[-1].start_time - INCUBATION_SIM_TIME
        secondary_cases = 0

        for c in self.contact_network.values():
            if c.start_time >= infectious_at:
                other = sim.human_agents[c.other_id]
                for sickness in other.sickness_records:
                    if sickness.start_time >= infectious_at:
                        secondary_cases += 1
                        break

        return secondary_cases


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
