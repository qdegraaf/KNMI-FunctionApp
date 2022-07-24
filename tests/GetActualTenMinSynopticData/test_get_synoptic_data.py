import pytest
from azure.core.exceptions import HttpResponseError

from GetActualTenMinSynopticData.errors import SynopticDataError


@pytest.mark.freeze_time("2022-01-01 12:00:00")
def test_upload_file_content_to_adls_raises_error_on_http_error(mock_processor, mocker):
    mock_processor.adls_client.create_file.side_effect = HttpResponseError("Oops")\

    with pytest.raises(SynopticDataError) as excinfo:
        mock_processor.upload_file_content_to_adls(data=b"somedata", filename="file.nc")

    assert str(excinfo.value) ==  "Unexpected HttpResponseError when attempting to upload file.nc to TestAccount. Full error: Oops"
