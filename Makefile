.PHONY: clean, install, install-dev, test, format, lint

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	find . -name '*.egg-info' | xargs rm -rf

install:
	pip install .

install-dev:
	pip install .[dev,test,lint]

# Testing
test:
	py.test tests/

# Formatting & Code strength

format:
	black GetActualTenMinSynopticData/ KNWToSQL/ storage/ loganalytics/ tests/


lint:
	ruff .

