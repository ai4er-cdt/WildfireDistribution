# Requirements

## Dependencies structure
This directory contains the environment setup to reproduce all code in this repository. 

- `environment.yml`: Is the general environment specification for deployment. Per default, this automatically installs `dev-requirements.txt` into the python environment.
- `dev-requirements.txt`: PIP requirements file for the packages needed for developing code (includes convenient dependencies, linters, formatters)  
- `test-requirements.txt`: PIP requirements file for the packages needed to run continuous integration (includes linting, unit test dependencies)  
- `requirements.txt`: PIP requirements file for the packages needed to run code for deployment (minimal dependencies only) 
