from os import environ

from azure.functions import TimerRequest

from loganalytics.law import LogAnalyticsWorkspaceLogger


class Processor:
    def __init__(
        self,
        logger: LogAnalyticsWorkspaceLogger,
    ):
        self.logger = logger

    def process(self, api_key: str):
        pass


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
