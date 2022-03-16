[<img align="right" src=report/figures/logos/phi_labs.png width=48px>](https://philab.phi.esa.int/)
[<img align="right" src=report/figures/logos/bas.png width=48px>](https://www.bas.ac.uk/)
[<img align="right" src=report/figures/logos/AI4ER.png width=47px>](https://ai4er-cdt.esc.cam.ac.uk/)
[<img align="right" src=report/figures/logos/bto_logo.png width=50px>](https://www.bto.org/)
[<img align="right" src=report/figures/logos/UoC_logo.png width=60px>](https://www.cam.ac.uk/)

# Using Convolutional Neural Networks for Wildfire Prediction in Polesia

 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
 <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

## 1.0 - Background
In late 2021, one of Cambridge's EPSRC-funded centre for doctoral training (CDT) program's by the name of 'AI for the study of environmental risks' (AI4ER) launched a group team challenge (GTC) amongst it's cohort of 2021. The cohort was split down the middle into two groups of 4, with one tasked with building a neural net capable of categorising ice and open water in the Antarctic's Bellinhausen Sea ('Ice Group'), whilst the other looked to create a neural net able to predict wildfire in the eastern European region of Polesia ('Fire Group'). Both of these projects were begun in December 2021 and due to end by March 2022.

The European Space Agency's (ESA) Φ-lab Division (of the Future Systems Department of the EO Programmes Directorate within ESA) spawned an initiative by the name of AI for earth observation (AI4EO) in 2019. It was in collaboration with this initiative that Cambridge's AI4ER program created the dual GTC projects- the 'ice group' benefitted from the domain-specific guidance of the British Antarctic Survey (BAS), whilst the 'fire group' was aided by the British Ornithological Trust (BTO).

## 2.0 - Aim
The aim of this project has been to identify spatial relationships between wildfire distribution and climatic, topographical, pedological drivers of wildfire. This was to be achieved by utilising convolutional neural networks (CNNs) to reduce the dimensionality of various geospatial datasets. The motivation for such an endeavour was to provide a new tool for prediction of wildfire genesis, perhaps facilitating the mitigation of future destructive wildfire events; which are known to cause damage to local ecosystems if too frequent.

To narrow the geospatial bounds of the project, a study area was defined which encompassed the north of Ukraine and the south of Belarus, the rough region being known by the name Polesia.

![Polesia Study Area](report/figures/study_area_illustration2.png?raw=true "Polesia in relation to Europe as a whole.")
Figure 1 - Polesia's bounds in relation to the rest of Europe. The magnification provides clearer bounds of both the Polesia project area and the land cover training sub-region in relation to the two countries of Belarus and Ukraine. The map used is provided by OpenStreetMaps under an [ODbL](https://opendatacommons.org/licenses/odbl/) [OSM, 2022] whilst the plotting itself was done by QGIS which is publicly available under the [GNU GPL](https://www.gnu.org/licenses/gpl-3.0.en.html) [QGIS, 2022].

## 3.0 - Data
### 3.1 - Target Dataset
As directed by partners of this project, the target dataset used was the ['Fire_cci Burned Area dataset'](https://geogra.uah.es/fire_cci/firecci51.php) as generated and served by the ESA. This dataset was originally derived from spectral band data from [MODIS](https://lpdaac.usgs.gov/products/mod09gqv006/) alongside thermal data from [MODIS active fire products](https://modis-fire.umd.edu/index.html). 
This dataset was processed into monthly batches and each pixel was assigned a (burn/no-burn) value (See Figure 2); this target dataset provided a necessary ground truth with which to iteratively improve the neural networks performance when processing the predictor datasets.
![Burn Coverage Polesia](report/figures/ModisBurnPlot_2020.png?raw=true "Burn Plot for March 2020 with burnt and unburnt apparent")
Figure 3 - Simplified plot of MODIS-derived Fire_CCI51 dataset, with burnt and unburnt areas apparent for month 3 of 2020.

### 3.2 - Predictor Datasets
3.2.1 - Landcover Types (Sentinel+Classifier)

Based on previous work commissioned by the BTO, an earth engine based land cover classifier built by [Artio Earth Observation LLP](https://find-and-update.company-information.service.gov.uk/company/OC437578) was made available to this project via a public [github page](https://github.com/tpfd/Polesia-Landcover). This classifier was based on a random forest (RF) classification algorithm which had been pre-trained for a sub-region of Polesia (See Figure 1). By using this algorithm on satellite imagery gathered by Sentinel, a full landcover map of the entire project area was generated (classifying pixels into one of nine simple landcover types) with a maximum spatial resolution of 20m (See Figure 3).
![Land Cover Polesia](report/figures/SimpleLandCoverMosaic_2018_2.png?raw=true "Land cover generated for Polesia")
Figure 3 - Land cover map for 2018 generated using the random forest model in combination with Sentinel satellite imagery.

3.2.2 - Surface Temperature, Snow Cover/Depth, Soil Moisture (ERA5)

To obtain datasets pertaining to potential climatological, cryological and pedological predictors of wildfires, [ERA5 reananalysis data](https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5) generated by the European Centre for Medium-Range Weather Forecasts ([ECMWF](https://www.ecmwf.int/)) was obtained. By selectively downloading and splitting apart ERA5 netCDF files it was possible to obtain three important predictor datasets: 2m surface temperature (K), snow cover, snow depth (m of water equivalent), and soil moisture (m<sup>3</sup> water m<sup>-3</sup> soil). All of the reanalysis datasets retained their 31km spatial resolution.



- what is this project about? 
- where to find the data and how to access it
- adding a note on the license: CC-BY for reports, readme etc.

## 4.0 - Requirements
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

- Campbell, Hamish. *(AI4ER Cohort-2021, University of Cambridge)*[<img align="right" src=report/figures/logos/GitHub-Mark.png width=30px>](https://github.com/Hamish-Cam)[<img align="right" src=report/figures/logos/AI4ER.png width=25px>](https://ai4er-cdt.esc.cam.ac.uk/StaffDirectory/students-all/2021-students)

- Colverd, Grace. *(AI4ER Cohort-2021, University of Cambridge)*[<img align="right" src=report/figures/logos/GitHub-Mark.png width=30px>](https://github.com/graceebc9)[<img align="right" src=report/figures/logos/AI4ER.png width=25px>](https://ai4er-cdt.esc.cam.ac.uk/StaffDirectory/students-all/2021-students)

- Højlund-Dodd, Thomas. *(AI4ER Cohort-2021, University of Cambridge)*[<img align="right" src=report/figures/logos/GitHub-Mark.png width=30px>](https://github.com/ThomasDodd97)[<img align="right" src=report/figures/logos/AI4ER.png width=25px>](https://ai4er-cdt.esc.cam.ac.uk/StaffDirectory/students-all/2021-students)[<img align="right" src=report/figures/logos/ORCID_iD.png width=25px>](https://orcid.org/0000-0001-9690-8627)

- Stefanović, Sofija. *(AI4ER Cohort-2021, University of Cambridge)*[<img align="right" src=report/figures/logos/GitHub-Mark.png width=30px>](https://github.com/sofstef)[<img align="right" src=report/figures/logos/AI4ER.png width=25px>](https://ai4er-cdt.esc.cam.ac.uk/StaffDirectory/students-all/2021-students)

Technical Support Members:

- Rogers, Martin. *(AI Lab, British Antarctic Survey (BAS), Cambridge)*[<img align="right" src=report/figures/logos/GitHub-Mark.png width=30px>](https://github.com/MartinSJRogers)[<img align="right" src=report/figures/logos/bas.png width=25px>](https://www.bas.ac.uk/profile/user_3491-2/)

- Wheeler, James. *(Phi Lab, European Space Agency (ESA))*[<img align="right" src=report/figures/logos/phi_labs.png width=25px>](https://philab.phi.esa.int/our-people/)

Domain Support Members:

- Ashton-Butt, Adham. *(British Trust for Ornithology (BTO))*[<img align="right" src=report/figures/logos/bto_logo.png width=25>](https://www.bto.org/about-bto/our-staff/adham-ashton-butt)

### Organisations

University of Cambridge:
- AI for the study of Environmental Risks (AI4ER), UKRI Centre for Doctoral Training, Cambridge.[<img align="right" src=report/figures/logos/AI4ER.png width=25px>](https://ai4er-cdt.esc.cam.ac.uk/)

AI4EO Initiative of ESA's Φ-Lab
- AI for Earth Observation (AI4EO) Initiative, Φ-lab Division of the Future Systems Department of the EO Programmes Directorate, European Space Agency (ESA).[<img align="right" src=report/figures/logos/ESA_logo_simple.png width=25px>](https://www.esa.int/)[<img align="right" src=report/figures/logos/phi_labs.png width=25px>](https://philab.phi.esa.int/)[<img align="right" src=report/figures/logos/ai4eo.png width=70px>](https://ai4eo.eu/)

AI4EO Partner:
- British Trust for Ornithology (BTO), Norfolk.[<img align="right" src=report/figures/logos/bto_logo.png width=25px>](https://www.bto.org/)

## References

OSM. (2022) 'Map of Europe' Available at: https://www.openstreetmap.org/about (Accessed: 14 March 2022)

QGIS. (2022) 'QGIS Version 3.22.3-Białowieża' Available at: https://www.qgis.org/en/site/forusers/download.html (Accessed: 14 March 2022)

---

Project template created by the [Cambridge AI4ER Cookiecutter](https://github.com/ai4er-cdt/ai4er-cookiecutter).