from setuptools import (
    find_packages,
    setup,
)

version = "1.0.0"

setup(
    name="KNMI-FA",
    description="Function App to run timed functions on the KNMI API",
    version=version,
    packages=find_packages(),
    install_requires=[
        "azure-functions==1.11.2",
    ],
)
