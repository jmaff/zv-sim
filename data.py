from agents import *
from simulator import seconds_to_sim_ticks


def convert_locations(input):
    path = {}
    for p in input:
        path[seconds_to_sim_ticks(p[0])] = LocationRecord(x=p[1], y=p[2])
    return path


def convert_reports(input):
    reports = {}
    for r in input:
        reports[seconds_to_sim_ticks(r[0])] = r[1]
        return reports


def build_human(id, locations, reports):
    return Human(
        id=id,
        location_history=convert_locations(locations),
        reports=convert_reports(reports),
    )


def build_animal(id, locations, radius, hazard_rate):
    return AnimalPresence(
        id=id,
        migration_pattern=convert_locations(locations),
        radius=radius,
        hazard_rate=hazard_rate,
    )


#### DATASET 0 ####
# Humans: 2
# Animal presences: 1
# H0 -> Animal contact, contacts H1 afterward
# H1 -> No animal contact
D0_H0_LOCATIONS = [
    (0, 100, 100),
    (200, 500, 100),
    (400, 500, 500),
    (600, 100, 500),
]  # contacts animal
D0_H0_REPORTS = [(380, HumanStatus.SICK)]
D0_H0 = build_human(0, D0_H0_LOCATIONS, D0_H0_REPORTS)

D0_H1_LOCATIONS = [
    (0, 200, 100),
    (200, 160, 100),
    (400, 490, 500),
    (600, 300, 500),
]  # contacts other human, does not contact animal
D0_H1_REPORTS = [(500, HumanStatus.SICK)]
D0_H1 = build_human(1, D0_H1_LOCATIONS, D0_H1_REPORTS)

D0_HUMANS = [D0_H0, D0_H1]

D0_A0_LOCATIONS = [(0, 450, 150)]
D0_A0_RADIUS = 100
D0_A0_HAZARD_RATE = 0.05
D0_A0 = build_animal(0, D0_A0_LOCATIONS, D0_A0_RADIUS, D0_A0_HAZARD_RATE)

D0_ANIMALS = [D0_A0]

#### DATASET 1 ####
# Humans: 2
# Animal presences: 1
# H0 -> Contacts H1, THEN has animal contact
# H1 -> No animal contact

#### DATASET 2 ####
# Humans: 4
# Animal presences: 2
# H0 -> No animal contact
# H1 -> Exposure to A0, none to A1
# H2 -> Exposure to A1, none to A0

# change motion model and compare cases
# change levels of reported / calculated spread
