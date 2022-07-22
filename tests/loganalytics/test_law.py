import base64
import hashlib
import hmac
import json

import httpretty
import pytest
from requests.adapters import Retry

from loganalytics.errors import (
    LogAnalyticsWorkspaceResponseError,
    LogAnalyticsWorkspaceRetryError,
    ValidationError,
)


@pytest.mark.freeze_time("2020-01-01")
def test_build_signature_builds_correct_signature(law_logger):
    string_format_of_test__log_data = json.dumps(
        {"message": "Test 1-2-3", "severity": 10}
    )

    message = (
        "POST\n"
        "41\n"
        "application/json\n"
        "x-ms-date:Wed, 01 Jan 2020 00:00:00 GMT\n"
        "/api/logs"
    )
    message_in_bytes = bytes(message, encoding="utf-8")
    test_key = base64.b64decode(law_logger._shared_key)
    signature = base64.b64encode(
        hmac.new(
            key=test_key,
            msg=message_in_bytes,
            digestmod=hashlib.sha256,
        ).digest()
    ).decode()

    result = law_logger._build_signature(string_format_of_test__log_data)

    assert result == signature
    assert isinstance(result, str)


@httpretty.activate
@pytest.mark.freeze_time("2020-01-01")
def test_log_builds_correct_request(law_logger, mocker):
    signature_mock = mocker.patch(
        "loganalytics.law.LogAnalyticsWorkspaceLogger._build_signature",
        return_value="test_signature",
    )
    httpretty.register_uri(
        httpretty.POST,
        "https://Test_workspace_id.ods.opinsights.azure.com/api/logs?api-version=2016-04-01",
        responses=[httpretty.Response(body="Success!", status=200)],
    )

    law_logger.log(message="Test 1-2-3", severity=10)

    signature_mock.assert_called_once_with('{"message": "Test 1-2-3", "severity": 10}')
    history = httpretty.latest_requests()
    assert len(history) == 1
    assert history[0].method == "POST"
    assert history[0].path == "/api/logs?api-version=2016-04-01"
    assert history[0].body == b'{"message": "Test 1-2-3", "severity": 10}'
    assert (
        history[0].headers.get("Authorization")
        == "SharedKey Test_workspace_id:test_signature"
    )
    assert history[0].headers.get("Content-Type") == "application/json"
    assert history[0].headers.get("Log-Type") == "Test_LAW"
    assert history[0].headers.get("x-ms-date") == "Wed, 01 Jan 2020 00:00:00 GMT"


def test_log_raises_validation_error_if_it_receives_wrong_log_types(law_logger):
    with pytest.raises(ValidationError) as excinfo:
        law_logger.log(message=123, severity="VERY BAD")

    assert (
        str(excinfo.value)
        == "Invalid types for log message. Expected message to be str and "
        "severity to be an int. Got: \nmessage: <class 'int'> \n"
        "severity: <class 'str'>"
    )


@httpretty.activate
@pytest.mark.freeze_time("2020-01-01")
def test__log_retries_on_503_response(law_logger, mocker):
    signature_mock = mocker.patch(
        "loganalytics.law.LogAnalyticsWorkspaceLogger._build_signature",
        return_value="test_signature",
    )
    httpretty.register_uri(
        httpretty.POST,
        "https://Test_workspace_id.ods.opinsights.azure.com/api/logs?api-version=2016-04-01",
        responses=[
            httpretty.Response(body='{"message": "Im not ready!"}', status=503),
            httpretty.Response(body='{"message": "Im not ready!"}', status=503),
            httpretty.Response(body='{"message": "Im not ready!"}', status=503),
            httpretty.Response(body='{"message": "Im Ready!"}', status=200),
        ],
    )
    law_logger._log(message="Test 1-2-3", severity=10)
    signature_mock.assert_called_once_with('{"message": "Test 1-2-3", "severity": 10}')
    history = httpretty.latest_requests()

    assert len(history) == 4

    for request in history:
        assert request.method == "POST"
        assert request.path == "/api/logs?api-version=2016-04-01"
        assert request.body == b'{"message": "Test 1-2-3", "severity": 10}'
        assert (
            request.headers.get("Authorization")
            == "SharedKey Test_workspace_id:test_signature"
        )
        assert request.headers.get("Content-Type") == "application/json"
        assert request.headers.get("Log-Type") == "Test_LAW"
        assert request.headers.get("x-ms-date") == "Wed, 01 Jan 2020 00:00:00 GMT"


@httpretty.activate
@pytest.mark.freeze_time("2020-01-01")
def test__log_raises_retry_error_after_too_many_retries_on_503_response(
    law_logger,
    mocker,
):
    signature_mock = mocker.patch(
        "loganalytics.law.LogAnalyticsWorkspaceLogger._build_signature",
        return_value="test_signature",
    )
    httpretty.register_uri(
        httpretty.POST,
        "https://Test_workspace_id.ods.opinsights.azure.com/api/logs?api-version=2016-04-01",
        responses=[
            httpretty.Response(body='{"message": "Im not ready!"}', status=503),
            httpretty.Response(body='{"message": "Im not ready!"}', status=503),
            httpretty.Response(body='{"message": "Im not ready!"}', status=503),
            httpretty.Response(body='{"message": "Im STILL not ready!"}', status=503),
        ],
    )

    with pytest.raises(LogAnalyticsWorkspaceRetryError) as error:
        law_logger._log(message="Test 1-2-3", severity=10)

    signature_mock.assert_called_once_with('{"message": "Test 1-2-3", "severity": 10}')

    history = httpretty.latest_requests()

    assert len(history) == 4
    assert "Still no successful request after 3 requests" in str(error.value)


@httpretty.activate
@pytest.mark.freeze_time("2020-01-01")
def test__log_raises_response_error_on_non_200_response(law_logger, mocker):
    signature_mock = mocker.patch(
        "loganalytics.law.LogAnalyticsWorkspaceLogger._build_signature",
        return_value="test_signature",
    )
    httpretty.register_uri(
        httpretty.POST,
        "https://Test_workspace_id.ods.opinsights.azure.com/api/logs?api-version=2016-04-01",
        responses=[
            httpretty.Response(body='{"message": "Im not ready!"}', status=503),
            httpretty.Response(body='{"message": "Im unexpected"}', status=404),
        ],
    )

    with pytest.raises(LogAnalyticsWorkspaceResponseError) as error:
        law_logger._log(message="Test 1-2-3", severity=10)

    signature_mock.assert_called_once_with('{"message": "Test 1-2-3", "severity": 10}')

    history = httpretty.latest_requests()

    assert len(history) == 2
    assert "Unexpected response with code 404" in str(error.value)


@httpretty.activate
@pytest.mark.freeze_time("2020-01-01")
def test__log_raises_calls_itself_recursively_on_invalid_signature_error(
    law_logger, mocker
):
    signature_mock = mocker.patch(
        "loganalytics.law.LogAnalyticsWorkspaceLogger._build_signature",
        return_value="test_signature",
    )
    httpretty.register_uri(
        httpretty.POST,
        "https://Test_workspace_id.ods.opinsights.azure.com/api/logs?api-version=2016-04-01",
        responses=[
            httpretty.Response(body='{"message": "Im not ready!"}', status=503),
            httpretty.Response(
                body='{"message": ""An invalid signature was specified in the Authorization header""}',  # noqa: E501
                status=403,
            ),
            httpretty.Response(body='{"message": "All good now!"}', status=200),
        ],
    )

    law_logger._log(message="Test 1-2-3", severity=10)

    # We expect 3 posts in total with 2 calls to build_signature as we have one recursive _log call
    sig_call_args = signature_mock.call_args_list
    assert len(sig_call_args) == 2
    for call in sig_call_args:
        assert call[0][0] == '{"message": "Test 1-2-3", "severity": 10}'

    history = httpretty.latest_requests()
    assert len(history) == 3


def test__configure_requests_session(law_logger, mocker, mock_http_adapter):
    retry_mock = mocker.patch("loganalytics.law.Retry", return_value=Retry(total=4242))
    adapter_mock = mocker.patch(
        "loganalytics.law.HTTPAdapter",
        return_value=mock_http_adapter,
    )

    session = law_logger._configure_requests_session(
        retries=123, retryable_error_codes={404}, backoff_factor=0.5
    )

    retry_mock.assert_called_once_with(
        total=123,
        status_forcelist={404},
        allowed_methods=["POST"],
        backoff_factor=0.5,
    )

    assert adapter_mock.call_args[1]["max_retries"].total == 4242

    assert len(session.adapters) == 2
    assert session.adapters["https://"] == mock_http_adapter
