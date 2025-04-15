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

D0_H1_LOCATIONS = [
    (0, 200, 100),
    (200, 160, 100),
    (400, 490, 500),
    (600, 300, 500),
]  # contacts other human, does not contact animal


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
