[![Tests & Coverage](https://github.com/qdegraaf/knmi-functionapp/actions/workflows/tests.yml/badge.svg)](https://github.com/qdegraaf/knmi-functionapp/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/qdegraaf/KNMI-FunctionApp/branch/main/graph/badge.svg?token=7BOWlltUMV)](https://codecov.io/gh/qdegraaf/KNMI-FunctionApp)

# Introduction 
KNMI-FA is a function app which contains the following functions:

- **GetActualTenMinSynopticData**: Queries the KNMI API every 10 minutes to get the latest synoptic
data files, list through them and store them locally


### Dependencies
Create a virtual environment for the project with e.g. pyenv.
```bash
pyenv virtualenv knmi-fa
pyenv activate knmi-fa
```

Afterwards install dependencies with 
```bash
make install
```

If you add, remove or update dependencies, make sure `setup.py` is updated and run
```bash
make requirements
```
to regenerate the requirements file.

### Tests
Tests for this project use pytest and can be run with
```bash
make test
```
after installing the requisite dependencies.

### Code Style & Strength
This repository uses various methods to maintain a consistent level of code quality. When adding a 
new feature or upgrading an existing one make sure to check the flake8 and mypy reports with 
```bash
make lint
```
