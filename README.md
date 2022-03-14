[<img align="right" src=report/figures/logos/ESA_logo_simple.png width=47px>](https://www.esa.int/)
[<img align="right" src=report/figures/logos/AI4ER.png width=47px>](https://ai4er-cdt.esc.cam.ac.uk/)
[<img align="right" src=report/figures/logos/bto_logo.png width=50px>](https://www.bto.org/)
[<img align="right" src=report/figures/logos/UoC_logo.png width=60px>](https://www.cam.ac.uk/)

# Wildfire Prediction

 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
 <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

## Project Focus

The aim of this project has been to identify spatial relationships between wildfire distribution and climatic, topographical, pedological drivers of wildfire.



- what is this project about? 
- where to find the data and how to access it
- who is supporting this project (add their logos maybe)
- adding a note on the license: CC-BY for reports, readme etc.

## Requirements
- Python 3.9+

## Getting started/installation

- how to set up the environment with the config file
- how to run the train script from the command line


## Example usage

- show some plots of results


## Project Organization
```
├── LICENSE
├── Makefile           <- Makefile with commands like `make init` or `make lint-requirements`
├── README.md          <- The top-level README for developers using this project.
|
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
|   |                     the creator's initials, and a short `-` delimited description, e.g.
|   |                     `1.0_jqp_initial-data-exploration`.
│   ├── exploratory    <- Notebooks for initial exploration.
│   └── reports        <- Polished notebooks for presentations or intermediate results.
│
├── report             <- Generated analysis as HTML, PDF, LaTeX, etc.
│   ├── figures        <- Generated graphics and figures to be used in reporting
│   └── sections       <- LaTeX sections. The report folder can be linked to your overleaf
|                         report with github submodules.
│
├── requirements       <- Directory containing the requirement files.
│
├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
├── src                <- Source code for use in this project.
│   ├── __init__.py    <- Makes src a Python module
│   │
│   ├── data_loading   <- Scripts to download or generate data
│   │
│   ├── preprocessing  <- Scripts to turn raw data into clean data and features for modeling
|   |
│   ├── models         <- Scripts to train models and then use trained models to make
│   │                     predictions
│   │
│   └── tests          <- Scripts for unit tests of your functions
│
└── setup.cfg          <- setup configuration file for linting rules
```

## Code formatting
To automatically format your code, make sure you have `black` installed (`pip install black`) and call
```black . ``` 
from within the project directory.

---

Project template created by the [Cambridge AI4ER Cookiecutter](https://github.com/ai4er-cdt/ai4er-cookiecutter).
