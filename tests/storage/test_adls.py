import pytest
from azure.identity import ManagedIdentityCredential

from storage.adls import get_adls_client


@pytest.mark.parametrize(
    "name,key,container",
    [
        ("pety", "the_happy", "container"),
        ("pety", ManagedIdentityCredential(), "container"),
    ],
)
def test_get_adls_client_correctly_formats_account_string(mocker, name, key, container):
    account_url = "https://pety.dfs.core.windows.net/"

    datalake_sc_mock = mocker.patch("storage.adls.DataLakeServiceClient")
    get_adls_client(name, key, container)

    datalake_sc_mock.assert_called_once_with(account_url=account_url, credential=key)
    datalake_sc_mock().get_file_system_client.assert_called_once_with(
        file_system=container
    )
