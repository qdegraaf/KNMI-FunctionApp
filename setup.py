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
        "azure-identity==1.10.0",
        "azure-storage-file-datalake==12.8.0",
        "psycopg2==2.9.3",
        "requests==2.28.1",
        "sqlalchemy==1.4.39",
    ],
)
