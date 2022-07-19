import base64
import datetime
import hashlib
import hmac
import json
from typing import Set

import requests
from requests.adapters import Retry
from requests.exceptions import RetryError
from requests.sessions import HTTPAdapter

from loganalytics.errors import ValidationError, LogAnalyticsWorkspaceRetryError, \
    LogAnalyticsWorkspaceResponseError


class LogAnalyticsWorkspaceLogger:
    """
    Logger class to send logs to LAW through HTTP API
    """

    def __init__(
        self,
        workspace_id: str,
        shared_key: str,
        custom_log_table_name: str,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        retryable_error_codes: Set[int] = {503},
    ):
        """
        :param workspace_id: workspace ID of Log Analytics Workspace in Azure
        :param shared_key: primary or secondary key in Log Analytics Workspace
        :param custom_log_table_name: table name of the custom log table in Log Analytics
          Workspace the table name will get "_CL" after the name in LAW. Does not allow '-'.
        :param max_retries: amount of times the LAWLogger will attempt to log a message before
          raising a LogAnalyticsWorkspaceError.
        :param backoff_factor: Factor to increase waiting time by between successive retries
          wait time is: {backoff factor} * (2 ** ({number of total retries} - 1)). See Retry docs
          for more info
        """
        self._workspace_id = workspace_id
        self._shared_key = shared_key
        self._custom_log_table_name = custom_log_table_name
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retryable_error_codes = retryable_error_codes
        self.session = self._configure_requests_session(
            retries=self.max_retries,
            retryable_error_codes=self.retryable_error_codes,
            backoff_factor=self.backoff_factor,
        )

    def log(self, message: str, severity: int):
        """
        Wrapper function for log call validates that message is always a str and severity is an int
        at runtime to avoid creating duplicate columns with differing types in LAW.

        :param message: The log message body
        :param severity: Severity of the log message.
        """
        if not isinstance(message, str) or not isinstance(severity, int):
            raise ValidationError(
                f"Invalid types for log message. Expected message to be str and "
                f"severity to be an int. Got: \n"
                f"message: {type(message)} \n"
                f"severity: {type(severity)}"
            )

        self._log(message, severity)

    def _log(self, message: str, severity: int):
        """
        Logs a message to Azure Log Analytics Workspace.

        NOTE: Raises HTTPError when status code of the response of the API call is not 200.
        :param message: The log message body
        :param severity: Severity of the log message. Follows the logging.INFO/WARNING/ERROR enum
        """
        json_data = {
            "message": message,
            "severity": severity,
        }

        data = json.dumps(json_data)

        try:
            # Making signature at the last possible moment before post, in case of tstamp mismatch
            signature = self._build_signature(data)
            response = self.session.post(
                url=(
                    f"https://{self._workspace_id}.ods.opinsights.azure.com/"
                    f"api/logs?api-version=2016-04-01"
                ),
                data=data,
                headers={
                    "Authorization": f"SharedKey {self._workspace_id}:{signature}",
                    "Content-Type": "application/json",
                    "Log-Type": self._custom_log_table_name,
                    "x-ms-date": datetime.datetime.utcnow().strftime(
                        "%a, %d %b %Y %H:%M:%S GMT",
                    ),
                },
            )
        except RetryError as e:
            raise LogAnalyticsWorkspaceRetryError(
                f"Still no successful request after {self.max_retries} requests.\n"
                f"URL: {e.request.url}\n"
                f"MSG: {e.strerror}\n"
                f"HEADERS: {e.request.headers}"
            )

        if response.status_code != 200:
            if (
                response.status_code == 403
                and "An invalid signature was specified in the Authorization header"
                in response.text
            ):
                # Because Azure sometimes temporarily bugs out and throws a 403 due to a bad
                # signature we want to retry the call. We cannot do this in the Retry of the
                # session because we need a new signature for this, so we recursively call the
                # function again to rebuild it. This could cause an infinite loop if the signature
                # is actually being built wrong. So keep an eye on this.
                # TODO: Replace with something more robust
                return self._log(message, severity)

            raise LogAnalyticsWorkspaceResponseError(
                f"Unexpected response with code {response.status_code}\n"
                f"URL: {response.url}\n"
                f"BODY: {response.text}\n"
                f"HEADERS: {response.headers}"
            )

    def _build_signature(self, data: str) -> str:
        """
        Builds a signature to authenticate an HTTP request to the HTTP Data Collector API from
        Azure.

        To authenticate a request the requests must be signed with a primary or secondary key
        found in Azure, and they have to be built in a specific way.
        :param data: json_data serialized to string format
        :return: HTTP Authentication signature string
        """
        # Date must be in this format, according to Microsoft:
        # Mon, 04 Apr 2016 08:00:00 GMT
        date_string_in_microsoft_format = datetime.datetime.utcnow().strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

        string_to_sign = (
            f"POST\n"
            f"{len(data)}\n"
            f"application/json\n"
            f"x-ms-date:{date_string_in_microsoft_format}\n"
            f"/api/logs"
        )
        message_in_bytes = bytes(string_to_sign, encoding="utf-8")

        # Base64 encode then decode is necessary to get hmac output to human readable string
        decoded_key = base64.b64decode(self._shared_key)
        signature = base64.b64encode(
            hmac.new(
                key=decoded_key,
                msg=message_in_bytes,
                digestmod=hashlib.sha256,
            ).digest()
        ).decode()

        return signature

    @staticmethod
    def _configure_requests_session(
        retries: int, retryable_error_codes: Set[int], backoff_factor: float
    ) -> requests.Session:
        session = requests.Session()
        retry_config = Retry(
            total=retries,
            status_forcelist=retryable_error_codes,
            allowed_methods=["POST"],
            backoff_factor=backoff_factor,
        )
        adapter = HTTPAdapter(max_retries=retry_config)
        session.mount("https://", adapter)
        return session
