[<img align="right" src=report/figures/logos/phi_labs.png width=48px>](https://philab.phi.esa.int/)
[<img align="right" src=report/figures/logos/bas.png width=48px>](https://www.bas.ac.uk/)
[<img align="right" src=report/figures/logos/AI4ER.png width=47px>](https://ai4er-cdt.esc.cam.ac.uk/)
[<img align="right" src=report/figures/logos/bto_logo.png width=50px>](https://www.bto.org/)
[<img align="right" src=report/figures/logos/UoC_logo.png width=60px>](https://www.cam.ac.uk/)

# Using Convolutional Neural Networks for Wildfire Prediction in Polesia

 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
 <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

## 1.0 - Background

In late 2021, one of Cambridge's EPSRC-funded centre for doctoral training (CDT) program's by the name of 'AI for the study of environmental risks' (AI4ER) launched a group team challenge (GTC)amongst it's cohort of 2021. The cohort was split down the middle into two groups of 4, with one tasked with building a neural net capable of categorising ice and open water in the Antarctic's Bellinhausen Sea, whilst the other looked to create a neural net able to predict wildfire in the eastern European region of Polesia.

Both of these projects were begun in December 2021 and due to end by March 2022

## 2.0 - Aim

The aim of this project has been to identify spatial relationships between wildfire distribution and climatic, topographical, pedological drivers of wildfire. This was to be achieved by utilising convolutional neural networks (CNNs) to reduce the dimensionality of various geospatial datasets. The motivation for such an endeavour was to provide a new tool for prediction of wildfire genesis, perhaps facilitating the mitigation of future destructive wildfire events; which are known to cause damage to local ecosystems if too frequent.

To narrow the geospatial bounds of the project, a study area was defined which encompassed the north of Ukraine and the south of Belarus, the rough region being known by the name Polesia.

![Polesia Study Area](report/figures/study_area_illustration.png?raw=true "Polesia in relation to Europe as a whole.")
<font size="1">Figure 1: Polesia's bounds in relation to the rest of Europe. The magnification provides clearer bounds of both Polesia and the Project Area in relation to Belarus and it's neighbour Ukraine. The map used is provided by OpenStreetMaps under an ODbL [OSM, 2022] whilst the plotting itself was done by QGIS which is publicly available under the GNU GPL [QGIS, 2022].</font>



- what is this project about? 
- where to find the data and how to access it
- who is supporting this project (add their logos maybe)
- adding a note on the license: CC-BY for reports, readme etc.

## 3.0 - Requirements
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

## Contributors & Organisations

### Contributors
Project Core Members:

- Campbell, Hamish. *(AI4ER Cohort-2021, University of Cambridge)*[<img align="right" src=report/figures/logos/GitHub-Mark.png width=30px>](https://github.com/Hamish-Cam)[<img align="right" src=report/figures/logos/AI4ER.png width=20px>](https://ai4er-cdt.esc.cam.ac.uk/StaffDirectory/students-all/2021-students)

- Colverd, Grace. *(AI4ER Cohort-2021, University of Cambridge)*[<img align="right" src=report/figures/logos/GitHub-Mark.png width=30px>](https://github.com/graceebc9)[<img align="right" src=report/figures/logos/AI4ER.png width=20px>](https://ai4er-cdt.esc.cam.ac.uk/StaffDirectory/students-all/2021-students)

- Højlund-Dodd, Thomas. *(AI4ER Cohort-2021, University of Cambridge)*[<img align="right" src=report/figures/logos/GitHub-Mark.png width=30px>](https://github.com/ThomasDodd97)[<img align="right" src=report/figures/logos/AI4ER.png width=20px>](https://ai4er-cdt.esc.cam.ac.uk/StaffDirectory/students-all/2021-students)[<img align="right" src=report/figures/logos/ORCID_iD.png width=20px>](https://orcid.org/0000-0001-9690-8627)

- Stefanović, Sofija. *(AI4ER Cohort-2021, University of Cambridge)*[<img align="right" src=report/figures/logos/GitHub-Mark.png width=30px>](https://github.com/sofstef)[<img align="right" src=report/figures/logos/AI4ER.png width=20px>](https://ai4er-cdt.esc.cam.ac.uk/StaffDirectory/students-all/2021-students)

Technical Support Members:

- Rogers, Martin. *(AI Lab, British Antarctic Survey (BAS), Cambridge)*[<img align="right" src=report/figures/logos/GitHub-Mark.png width=30px>](https://github.com/MartinSJRogers)[<img align="right" src=report/figures/logos/bas.png width=21px>](https://www.bas.ac.uk/profile/user_3491-2/)

- Wheeler, James. *(Phi Lab, European Space Agency (ESA))*[<img align="right" src=report/figures/logos/phi_labs.png width=24px>](https://philab.phi.esa.int/our-people/)

Domain Support Members:

- Ashton-Butt, Adham. *(British Trust for Ornithology (BTO))*[<img align="right" src=report/figures/logos/bto_logo.png width=26>](https://www.bto.org/about-bto/our-staff/adham-ashton-butt)

### Organisations:

University of Cambridge:
- AI for the study of Environmental Risks (AI4ER), UKRI Centre for Doctoral Training, Cambridge.[<img align="right" src=report/figures/logos/AI4ER.png width=17px>](https://ai4er-cdt.esc.cam.ac.uk/)

AI4EO Initiative of ESA's Φ-Lab
- AI for Earth Observation (AI4EO) Initiative, Φ-lab Division of the Future Systems Department of the EO Programmes Directorate, European Space Agency (ESA).[<img align="right" src=report/figures/logos/ESA_logo_simple.png width=24px>](https://www.esa.int/)[<img align="right" src=report/figures/logos/phi_labs.png width=24px>](https://philab.phi.esa.int/)[<img align="right" src=report/figures/logos/ai4eo.png width=70px>](https://ai4eo.eu/)

AI4EO Partner:
- British Trust for Ornithology (BTO), Norfolk.[<img align="right" src=report/figures/logos/bto_logo.png width=26px>](https://www.bto.org/)

## References

OSM. (2022) 'Map of Europe' Available at: https://www.openstreetmap.org/about (Accessed: 14 March 2022)

QGIS. (2022) 'QGIS Version 3.22.3-Białowieża' Available at: https://www.qgis.org/en/site/forusers/download.html (Accessed: 14 March 2022)

---

Project template created by the [Cambridge AI4ER Cookiecutter](https://github.com/ai4er-cdt/ai4er-cookiecutter).