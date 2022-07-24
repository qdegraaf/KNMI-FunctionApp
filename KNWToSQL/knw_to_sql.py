from os import environ

from azure.functions import InputStream
from sqlalchemy.orm import Session

from loganalytics.law import LogAnalyticsWorkspaceLogger
from storage.postgres import create_psql_session


class Processor:
    def __init__(
        self,
        logger: LogAnalyticsWorkspaceLogger,
        sql_session: Session,
    ):
        self.logger = logger
        self.sql_session = sql_session

    def process(self):
        pass


# Azure typechecks this signature. So do not touch it
def main(blob: InputStream):
    azure_logger = LogAnalyticsWorkspaceLogger(
        workspace_id=environ["LAWID"],
        shared_key=environ["LAWKEY"],
        custom_log_table_name="GetActualTenMinSynopticData",
    )
    psql_session = create_psql_session(
        username=environ["PSQLUSERNAME"],
        password=environ["PSQLPASSWORD"],
        host=environ["PSQLHOST"]
    )
    proc = Processor(
        logger=azure_logger,
        sql_session=psql_session,
    )
    proc.process()