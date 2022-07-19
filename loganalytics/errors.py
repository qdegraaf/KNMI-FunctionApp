from requests import HTTPError


class ValidationError(Exception):
    pass


class LogAnalyticsWorkspaceResponseError(HTTPError):
    pass


class LogAnalyticsWorkspaceRetryError(HTTPError):
    pass
