from typing import Union

from azure.identity import ManagedIdentityCredential
from azure.storage.filedatalake import FileSystemClient, DataLakeServiceClient

AccountKey = str


def get_adls_client(
    account_name: str,
    account_key: Union[AccountKey, ManagedIdentityCredential],
    container: str,
) -> FileSystemClient:
    """
    Return a FileSystemClient for a specific container

    :param account_name: Name of storage account
    :param account_key: Key used to access the container. If an AccountKey (str) is passed it will
      connect to the SA with URL and Key. If a ManagedIdentityCredential is passed instead this is
      used for connection
    :param container: Container to get client for
    :return: FileSystemClient for specific container
    """
    account_url = "https://{}.dfs.core.windows.net/".format(account_name)
    adls_client = DataLakeServiceClient(account_url=account_url, credential=account_key)
    file_system_client = adls_client.get_file_system_client(file_system=container)

    return file_system_client
