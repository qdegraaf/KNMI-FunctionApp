from enum import (
    Enum,
    EnumMeta,
)
from os.path import splitext


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True


class KNMIFileExtensions(Enum, metaclass=MetaEnum):
    NC = ".nc"
    HDF5 = ".hdf5"
    CSV = ".csv"


def validate_file_extension(filepath: str) -> bool:
    file_ext = splitext(filepath)[1]
    if file_ext not in KNMIFileExtensions:
        return False
    return True
