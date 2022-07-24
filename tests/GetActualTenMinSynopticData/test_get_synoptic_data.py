import pytest
from azure.core.exceptions import HttpResponseError
from requests import HTTPError

from GetActualTenMinSynopticData.errors import SynopticDataError


def test_get_file_list_returns_file_list_on_200(mock_processor, requests_mock):
    requests_mock.get(
        url="https://api.dataplatform.knmi.nl/open-data/v1/datasets/Actuele10mindataKNMIstations"
        "/versions/2/files",
        status_code=200,
        json={"files": [{"filename": "file1"}, {"filename": "file2"}]},
    )

    result = mock_processor.get_file_list("testKey")

    assert result == [{"filename": "file1"}, {"filename": "file2"}]

    mock_processor.logger.log.assert_called_with(
        message="Successfully got 2 filenames from: https://api.dataplatform.knmi.nl/open-data/v1/"
        "datasets/Actuele10mindataKNMIstations/versions/2/files",
        severity=20,
    )


def test_get_file_list_raises_error_on_invalid_status_code(
    mock_processor, requests_mock
):
    requests_mock.get(
        url="https://api.dataplatform.knmi.nl/open-data/v1/datasets/Actuele10mindataKNMIstations"
        "/versions/2/files",
        status_code=500,
    )

    with pytest.raises(SynopticDataError) as excinfo:
        mock_processor.get_file_list("testKey")

    assert (
        str(excinfo.value)
        == "Unexpected status code 500 for getting file list from URI: "
        "https://api.dataplatform.knmi.nl/open-data/v1/datasets/Actuele"
        "10mindataKNMIstations/versions/2/files Content: b''"
    )


def test_get_file_list_raises_error_on_http_error(mock_processor, requests_mock):
    requests_mock.get(
        url="https://api.dataplatform.knmi.nl/open-data/v1/datasets/Actuele10mindataKNMIstations"
        "/versions/2/files",
        exc=HTTPError("Oops"),
    )

    with pytest.raises(SynopticDataError) as excinfo:
        mock_processor.get_file_list("testKey")

    assert (
        str(excinfo.value) == "Unexpected HTTPError while getting file list from "
        "https://api.dataplatform.knmi.nl/open-data/v1/datasets/Actuele"
        "10mindataKNMIstations/versions/2/files: Oops"
    )


def test_get_file_content_requests_data_from_content_url_on_200(
    mock_processor, requests_mock
):
    requests_mock.get(
        url="https://api.dataplatform.knmi.nl/open-data/v1/datasets/Actuele10mindataKNMIstations/"
        "versions/2/files/file.nc/url",
        status_code=200,
        json={"temporaryDownloadUrl": "https://download.me"},
    )

    requests_mock.get(url="https://download.me", status_code=200, content=b"content")

    result = mock_processor.get_file_content("file.nc", "testKey")
    assert result == b"content"


def test_get_file_content_raises_error_on_invalid_status_code_for_get_content(
    mock_processor, requests_mock
):
    requests_mock.get(
        url="https://api.dataplatform.knmi.nl/open-data/v1/datasets/Actuele10mindataKNMIstations/"
        "versions/2/files/file.nc/url",
        status_code=200,
        json={"temporaryDownloadUrl": "https://download.me"},
    )

    requests_mock.get(
        url="https://download.me",
        exc=HTTPError("Oops"),
    )

    with pytest.raises(SynopticDataError) as excinfo:
        mock_processor.get_file_content("file.nc", "testKey")

    assert (
        str(excinfo.value)
        == "Unexpected HTTPError while getting content from url https://download.me: Oops"
    )


def test_get_file_content_raises_error_on_http_error_for_get_content(
    mock_processor, requests_mock
):
    requests_mock.get(
        url="https://api.dataplatform.knmi.nl/open-data/v1/datasets/Actuele10mindataKNMIstations/"
        "versions/2/files/file.nc/url",
        status_code=200,
        json={"temporaryDownloadUrl": "https://download.me"},
    )

    requests_mock.get(
        url="https://download.me",
        status_code=500,
    )

    with pytest.raises(SynopticDataError) as excinfo:
        mock_processor.get_file_content("file.nc", "testKey")

    assert (
        str(excinfo.value)
        == "Unexpected status code 500 for getting content from url https://download.me "
        "Content: b''"
    )


def test_get_file_content_raises_error_on_invalid_status_code_for_get_url(
    mock_processor, requests_mock
):
    requests_mock.get(
        url="https://api.dataplatform.knmi.nl/open-data/v1/datasets/Actuele10mindataKNMIstations/"
        "versions/2/files/file.nc/url",
        status_code=500,
    )

    with pytest.raises(SynopticDataError) as excinfo:
        mock_processor.get_file_content("file.nc", "testKey")

    assert (
        str(excinfo.value)
        == "Unexpected status code 500 for getting content URL from URI: https://api.dataplatform"
        ".knmi.nl/open-data/v1/datasets/Actuele10mindataKNMIstations/versions/2/files/"
        "file.nc/url Content: b''"
    )


def test_get_file_content_raises_error_on_http_error(mock_processor, requests_mock):
    requests_mock.get(
        url="https://api.dataplatform.knmi.nl/open-data/v1/datasets/Actuele10mindataKNMIstations/"
        "versions/2/files/file.nc/url",
        exc=HTTPError("Oops"),
    )

    with pytest.raises(SynopticDataError) as excinfo:
        mock_processor.get_file_content("file.nc", "testKey")

    assert (
        str(excinfo.value)
        == "Unexpected HTTPError while getting content URL from https://api."
        "dataplatform.knmi.nl/open-data/v1/datasets/Actuele10mindataKNMI"
        "stations/versions/2/files/file.nc/url: Oops"
    )


@pytest.mark.freeze_time("2022-01-01 12:00:00")
def test_upload_file_content_to_adls_raises_error_on_http_response_error_for_get_url(
    mock_processor,
):
    mock_processor.adls_client.create_file.side_effect = HttpResponseError("Oops")

    with pytest.raises(SynopticDataError) as excinfo:
        mock_processor.upload_file_content_to_adls(data=b"somedata", filename="file.nc")

    assert (
        str(excinfo.value)
        == "Unexpected HttpResponseError when attempting to upload file.nc to TestAccount. "
        "Full error: Oops"
    )


@pytest.mark.freeze_time("2022-01-01 12:00:00")
def test_upload_file_formats_correct_path_and_logs_result(mock_processor, mocker):
    mock_create_file = mocker.MagicMock()
    mock_processor.adls_client.create_file.return_value = mock_create_file
    mock_processor.upload_file_content_to_adls(data=b"somedata", filename="file.nc")

    mock_processor.adls_client.create_file.assert_called_once_with(
        "nc/2022/01/01/12/file.nc"
    )
    mock_create_file.upload_data.assert_called_once_with(
        data=b"somedata", overwrite=True
    )

    mock_processor.logger.log.assert_called_with(
        message="Successfully uploaded file file.nc to TestAccount",
        severity=20,
    )
