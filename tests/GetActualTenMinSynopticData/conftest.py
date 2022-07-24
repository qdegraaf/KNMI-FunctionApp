import pytest

from GetActualTenMinSynopticData.get_synoptic_data import Processor


@pytest.fixture
def mock_processor(mocker):
    return Processor(
        mocker.MagicMock(),
        mocker.MagicMock(),
    )
