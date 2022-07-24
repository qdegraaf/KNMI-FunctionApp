from enum import Enum

import pytest

from GetActualTenMinSynopticData.models import (
    MetaEnum,
    validate_file_extension,
)


@pytest.mark.parametrize(
    "fp,result",
    [
        ("some_path.txt", False),
        ("some_path.hdf5", True),
        ("nopath", False),
        ("", False),
        ("double.path.txt", False),
        ("double.path.csv", True),
        ("thenc.nc", True),
    ],
)
def test_validate_file_extension(fp, result):
    assert validate_file_extension(fp) == result


@pytest.mark.parametrize(
    "inattr,result",
    [
        ("in", True),
        ("out", False),
        ("", False),
        (1, False),
    ],
)
def test_meta_enum(inattr, result):
    class MockEnum(Enum, metaclass=MetaEnum):
        IN = "in"

    assert (inattr in MockEnum) == result
