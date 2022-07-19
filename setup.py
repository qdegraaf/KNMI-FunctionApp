from setuptools import (
    find_packages,
    setup,
)

version = "1.0.0"

KNMI_API_ROOT = "https://api.dataplatform.knmi.nl/open-data/v1"

setup(
    name="KNMI-FA",
    description="Function App to run timed functions on the KNMI API",
    version=version,
    packages=find_packages(),
    install_requires=[
        "azure-functions==1.11.2",
        "requests==2.28.1",
    ],
)
