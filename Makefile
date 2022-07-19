.PHONY: clean, install, requirements, test, format, lint

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	find . -name '*.egg-info' | xargs rm -rf

install:
	pip install -r requirements_dev.txt

requirements:
	pip install pip-tools
	pip-compile

# Testing
test:
	py.test tests/

# Formatting & Code strength

format:
	black GetActualTenMinSynopticData/ loganalytics/ tests/ setup.py
	isort GetActualTenMinSynopticData loganalytics tests setup.py


lint:
	flake8 & mypy --config-file=mypy.ini .

