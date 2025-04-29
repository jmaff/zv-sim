# ZV-Sim: Probabilistic Simulation Framework for Pre-emergent Novel Zoonose Tracking

ZV-Sim is an open-source, modular Python framework for probabilistic simulation and analysis of pre-emergent novel zoonotic diseases using pervasive sensing data.

## Setup
`pip install -r requirements.txt`

## Running an Experiment
In `simulator.py`, configure the following values as needed for your dataset:

- `GRID_WIDTH`, `GRID_HEIGHT`
- `SIM_TICK_TIME_SECONDS`
- `STOP_SIM_AFTER`

In `data.py`, create arrays of `Human` and `AnimalPresence` agents that are initialized with your data, similar to provided examples. 

Modify `trial()` in `simulator.py` so that the following block instead assigns your arrays to `humans` and `animals`

```
animals = copy.deepcopy(YOUR_ARRAY_HERE)
humans = copy.deepcopy(YOUR_ARRAY_HERE)
```

Lastly, set the following values. These will often vary between experiments, and are used to organized output data:

- `USE_DISPLAY`
- `SAVE_DATA`
- `NUM_TRIALS`
- `MOTION_MODEL_DESC`
- `DATASET_DESC`

Run `python simulator.py`. Results will be written to `data/` in the root directory of the repo. 