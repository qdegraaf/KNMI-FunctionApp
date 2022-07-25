import csv
import logging
from io import StringIO
from os import environ
from typing import (
    Dict,
    List,
)

from azure.functions import InputStream
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from KNWToSQL.errors import KNWError
from KNWToSQL.models import KNWData
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

    def process(self, file: InputStream):
        rows = self.read_file_into_dicts(file)
        for row in rows:
            entry = KNWData(
                dtg=row["DTG"],
                f010=row["F010"],
                d010=row["D010"],
                to10=row["To10"],
                q010=row["Q010"],
                p010=row["P010"],
                f020=row["F020"],
                d020=row["D020"],
                to20=row["To20"],
                q020=row["Q020"],
                p020=row["P020"],
                f040=row["F040"],
                d040=row["D040"],
                to40=row["To40"],
                q040=row["Q040"],
                p040=row["P040"],
                f060=row["F060"],
                d060=row["D060"],
                to60=row["To60"],
                q060=row["Q060"],
                p060=row["P060"],
                f080=row["F080"],
                d080=row["D080"],
                to80=row["To80"],
                q080=row["Q080"],
                p080=row["P080"],
                f100=row["F100"],
                d100=row["D100"],
                t100=row["T100"],
                q100=row["Q100"],
                p100=row["P100"],
                f150=row["F150"],
                d150=row["D150"],
                t150=row["T150"],
                q150=row["Q150"],
                p150=row["P150"],
                f200=row["F200"],
                d200=row["D200"],
                t200=row["T200"],
                q200=row["Q200"],
                p200=row["P200"],
            )
            self.sql_session.add(entry)
        try:
            self.sql_session.commit()
        except SQLAlchemyError as e:
            self.logger.log(
                message=f"Encountered unexpected SQLAlchemyError: {str(e)}",
                severity=logging.ERROR,
            )
            self.sql_session.rollback()
            raise

    def read_file_into_dicts(self, file: InputStream) -> List[Dict]:
        self.logger.log(
            message=f"Converting {file.name} to dicts",
            severity=logging.INFO,
        )
        csv_data = StringIO(file.read().decode())
        # Skip first 8 rows of header info
        for i in range(8):
            csv_data.__next__()

        dicts = csv.DictReader(csv_data)
        # remove silly characters from column names
        if not dicts.fieldnames:
            raise KNWError(f"Could not get fieldnames for file: {file.name}")

        dicts.fieldnames = [x.replace("#", "").strip() for x in dicts.fieldnames]

        return list(dicts)


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
        host=environ["PSQLHOST"],
    )
    proc = Processor(
        logger=azure_logger,
        sql_session=psql_session,
    )
    proc.process(blob)
