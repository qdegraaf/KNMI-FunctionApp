import logging
from datetime import datetime
from os import environ
from os.path import splitext
from typing import (
    Dict,
    List,
    Union,
)

import requests
from azure.core.exceptions import HttpResponseError
from azure.functions import TimerRequest
from azure.storage.filedatalake import FileSystemClient
from requests import HTTPError

from GetActualTenMinSynopticData.errors import (
    SynopticDataError,
    SynopticDataValidationError,
)
from GetActualTenMinSynopticData.models import validate_file_extension
from loganalytics.law import LogAnalyticsWorkspaceLogger
from storage.adls import get_adls_client

KNMI_API_ROOT = "https://api.dataplatform.knmi.nl/open-data/v1"

SYNOPTIC_ENDPOINT = (
    f"{KNMI_API_ROOT}/datasets/Actuele10mindataKNMIstations/versions/2/files"
)


class Processor:
    def __init__(
        self,
        logger: LogAnalyticsWorkspaceLogger,
        adls_client: FileSystemClient,
    ):
        self.logger = logger
        self.adls_client = adls_client

    def process(self, api_key: str):
        file_list = self.get_file_list(api_key)
        for f in file_list:
            fname = f["filename"]
            if not isinstance(fname, str):
                raise SynopticDataValidationError(
                    f"Invalid type {type(fname)}: for {fname}"
                )
            if not validate_file_extension(fname):
                raise SynopticDataValidationError(f"Invalid file extension for file: {fname}")
            file_content = self.get_file_content(fname, api_key)
            self.upload_file_content_to_adls(data=file_content, filename=fname)

    def get_file_list(self, api_key: str) -> List[Dict[str, Union[str, int]]]:
        """Get list of files from KNMI API. Example response from KNMI API:
        {
            "isTruncated": true,
            "resultCount": 1,
            "files": [
                {
                "filename": "KMDS__OPER_P___10M_OBS_L2_202207152330.nc",
                "size": 189297,
                "lastModified": "2022-07-16T00:06:46+00:00"
                },
            ],
            "maxResults": 10,
            "startAfterFilename": ""
        }"""
        headers = {"Authorization": api_key}

        try:
            resp = requests.get(url=SYNOPTIC_ENDPOINT, headers=headers)
        except HTTPError as err:
            raise SynopticDataError(
                f"Unexpected HTTPError while getting file list from {SYNOPTIC_ENDPOINT}: "
                f"{str(err)}"
            )
        if resp.status_code == 200:
            self.logger.log(
                message=f"Successfully got {len(resp.json()['files'])} filenames from: "
                f"{SYNOPTIC_ENDPOINT}",
                severity=logging.INFO,
            )
            # TODO: KNMI Returns is_truncated value. Use this to determine if theres more files
            #  to get then get these. For now just grab whatever comes in
            return resp.json()["files"]

        else:
            raise SynopticDataError(
                f"Unexpected status code {resp.status_code} for getting content from "
                f"URI: {SYNOPTIC_ENDPOINT} Content: {str(resp.content)}"
            )

    def get_file_content(self, filename: str, api_key: str) -> bytes:
        """Get file content of a specific KNMI files"""
        url = f"{SYNOPTIC_ENDPOINT}/{filename}/url"
        headers = {"Authorization": api_key}
        try:
            resp = requests.get(url=url, headers=headers)
        except HTTPError as err:
            raise SynopticDataError(
                f"Unexpected HTTPError while getting content URL from {url}: {str(err)}"
            )
        if resp.status_code == 200:
            self.logger.log(
                message=f"Successfully got content url for {filename} from: {url}",
                severity=logging.INFO,
            )
            content_url = resp.json()["temporaryDownloadUrl"]
            try:
                file_resp = requests.get(content_url)
            except HTTPError as err:
                raise SynopticDataError(
                    f"Unexpected HTTPError while getting content from {content_url}: {str(err)}"
                )

            if resp.status_code == 200:
                return file_resp.content
            else:
                raise SynopticDataError(
                    f"Unexpected status code {resp.status_code} for getting content from url "
                    f"{content_url} Content: {str(resp.content)}"
                )
        else:
            raise SynopticDataError(
                f"Unexpected status code {resp.status_code} for getting content URL from "
                f"URI: {url} Content: {str(resp.content)}"
            )

    def upload_file_content_to_adls(self, data: bytes, filename: str):
        self.logger.log(message=f"Uploading file: {filename}", severity=logging.INFO)
        current_hour = datetime.utcnow().strftime("%Y/%m/%d/%H")
        upload_path = f"{splitext(filename)[1]}{current_hour}/{filename}"
        try:
            f = self.adls_client.create_file(upload_path)
            # TODO: Check if types match for data from KNMI and what Azure expects/allows for blob
            f.upload_data(data=data, overwrite=True)  # type: ignore
        except HttpResponseError as e:
            # TODO: We might not want to fail on one failed upload, consider retrying or uploading
            #  other files before raising
            raise SynopticDataError(
                f"Unexpected HttpResponseError when attempting to upload {filename} to "
                f"{self.adls_client.account_name}. Full error: {str(e)}"
            )
        self.logger.log(
            message=f"Successfully uploaded file {filename} to {self.adls_client.account_name}",
            severity=logging.INFO,
        )


# Azure typechecks this signature. So do not touch it
def main(timer: TimerRequest):
    azure_logger = LogAnalyticsWorkspaceLogger(
        workspace_id=environ["LAWID"],
        shared_key=environ["LAWKEY"],
        custom_log_table_name="GetActualTenMinSynopticData",
    )
    adls_client = get_adls_client(
        account_name=environ["ADLSACCOUNTNAME"],
        account_key=environ["ADLSACCOUNTKEY"],
        container="knmisynoptic",
    )
    proc = Processor(logger=azure_logger, adls_client=adls_client)
    try:
        proc.process(environ["KNMIAPIKEY"])
    except (SynopticDataError, SynopticDataValidationError) as e:
        proc.logger.log(
            message=f"Unexpected Error when getting KNMI data Full error: {str(e)}",
            severity=logging.ERROR,
        )
        raise
