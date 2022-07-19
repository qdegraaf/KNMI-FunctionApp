import logging
from os import environ
from typing import (
    Dict,
    List,
    Union,
)

import requests
from azure.functions import TimerRequest
from requests import HTTPError

from GetActualTenMinSynopticData.errors import SynopticDataError
from loganalytics.law import LogAnalyticsWorkspaceLogger
from setup import KNMI_API_ROOT

SYNOPTIC_ENDPOINT = (
    f"{KNMI_API_ROOT}/datasets/Actuele10mindataKNMIstations/versions/2/files"
)


class Processor:
    def __init__(
        self,
        logger: LogAnalyticsWorkspaceLogger,
    ):
        self.logger = logger

    def process(self, api_key: str):
        file_list = self.get_file_list(api_key)
        for f in file_list:
            file_content = self.get_file_content(f["filename"], api_key)  # type: ignore
            # TODO: Write file content somewhere

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
            self.logger.log(
                message=f"Unexpected HTTPError while getting file list from {SYNOPTIC_ENDPOINT}: "
                f"{str(err)}",
                severity=logging.ERROR,
            )
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
            self.logger.log(
                message=f"Unexpected HTTPError while getting content URL from {url}: {str(err)}",
                severity=logging.ERROR,
            )
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
                self.logger.log(
                    message=f"Unexpected HTTPError while getting content from {content_url}:"
                    f" {str(err)}",
                    severity=logging.ERROR,
                )
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


# Azure typechecks this signature. So do not touch it
def main(timer: TimerRequest):
    azure_logger = LogAnalyticsWorkspaceLogger(
        workspace_id=environ["LAWID"],
        shared_key=environ["LAWKEY"],
        custom_log_table_name="GetActualTenMinSynopticData",
    )
    proc = Processor(
        logger=azure_logger,
    )
    proc.process(environ["KNMIAPIKEY"])
