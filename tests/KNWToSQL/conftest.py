from os import path

import pytest

from KNWToSQL.knw_to_sql import Processor


def get_file(filepath: str):
    """Return the absolute path to a test file."""
    return path.join(path.dirname(__file__), filepath)


@pytest.fixture
def mock_processor(mocker):
    return Processor(
        mocker.MagicMock(),
        mocker.MagicMock(),
    )


@pytest.fixture
def mock_input_stream(mocker):
    mock = mocker.MagicMock()
    mock.name = "knw.csv"
    with open(get_file(filepath="files/mockknwfile.csv"), "rb") as fdata:
        mock.read.return_value = fdata.read()
    return mock


@pytest.fixture
def mock_empty_input_stream(mocker):
    mock = mocker.MagicMock()
    mock.name = "knw.csv"
    with open(get_file(filepath="files/emptymockknwfile.csv"), "rb") as fdata:
        mock.read.return_value = fdata.read()
    return mock


@pytest.fixture
def mock_row():
    return {
        "DTG": "2022-01-01 13:00",
        "F010": "1.2",
        "D010": "2.2",
        "T010": "3.2",
        "Q010": "4.2",
        "P010": "3.2",
        "F020": "2.2",
        "D020": "1.2",
        "T020": "4.2",
        "Q020": "4.2",
        "P020": "4.2",
        "F040": "4.2",
        "D040": "4.2",
        "T040": "4.2",
        "Q040": "4.2",
        "P040": "4.2",
        "F060": "4.2",
        "D060": "4.2",
        "T060": "4.2",
        "Q060": "4.2",
        "P060": "4.2",
        "F080": "4.2",
        "D080": "4.2",
        "T080": "4.2",
        "Q080": "4.2",
        "P080": "4.2",
        "F100": "4.2",
        "D100": "4.2",
        "T100": "4.2",
        "Q100": "4.2",
        "P100": "4.2",
        "F150": "4.2",
        "D150": "4.2",
        "T150": "4.2",
        "Q150": "4.2",
        "P150": "4.2",
        "F200": "4.2",
        "D200": "4.2",
        "T200": "4.2",
        "Q200": "4.2",
        "P200": "4.2",
    }
