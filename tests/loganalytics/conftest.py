import pytest
from requests.adapters import Retry
from requests.sessions import HTTPAdapter

from loganalytics.law import LogAnalyticsWorkspaceLogger


@pytest.fixture
def law_logger() -> LogAnalyticsWorkspaceLogger:
    return LogAnalyticsWorkspaceLogger(
        workspace_id="Test_workspace_id",
        shared_key="test_key==",
        custom_log_table_name="Test_LAW",
        max_retries=3,
        backoff_factor=0.1,
        retryable_error_codes={503},
    )


@pytest.fixture
def mock_http_adapter() -> HTTPAdapter:
    retry_config = Retry(
        total=2,
        status_forcelist=[404],
    )
    return HTTPAdapter(max_retries=retry_config)
