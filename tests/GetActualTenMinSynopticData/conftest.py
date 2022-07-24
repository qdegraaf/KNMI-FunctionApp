import pytest

from GetActualTenMinSynopticData.get_synoptic_data import Processor


@pytest.fixture
def mock_processor(mocker):
    proc = Processor(
        mocker.MagicMock(),
        mocker.MagicMock(),
    )
    proc.adls_client.account_name = "TestAccount"
    return proc
