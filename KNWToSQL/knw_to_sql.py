import csv
import logging
from datetime import datetime
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
                dtg=datetime.strptime(row["DTG"], "%Y-%m-%d %H:%M"),
                f010=float(row["F010"]),
                d010=float(row["D010"]),
                t010=float(row["T010"]),
                q010=float(row["Q010"]),
                p010=float(row["P010"]),
                f020=float(row["F020"]),
                d020=float(row["D020"]),
                t020=float(row["T020"]),
                q020=float(row["Q020"]),
                p020=float(row["P020"]),
                f040=float(row["F040"]),
                d040=float(row["D040"]),
                t040=float(row["T040"]),
                q040=float(row["Q040"]),
                p040=float(row["P040"]),
                f060=float(row["F060"]),
                d060=float(row["D060"]),
                t060=float(row["T060"]),
                q060=float(row["Q060"]),
                p060=float(row["P060"]),
                f080=float(row["F080"]),
                d080=float(row["D080"]),
                t080=float(row["T080"]),
                q080=float(row["Q080"]),
                p080=float(row["P080"]),
                f100=float(row["F100"]),
                d100=float(row["D100"]),
                t100=float(row["T100"]),
                q100=float(row["Q100"]),
                p100=float(row["P100"]),
                f150=float(row["F150"]),
                d150=float(row["D150"]),
                t150=float(row["T150"]),
                q150=float(row["Q150"]),
                p150=float(row["P150"]),
                f200=float(row["F200"]),
                d200=float(row["D200"]),
                t200=float(row["T200"]),
                q200=float(row["Q200"]),
                p200=float(row["P200"]),
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

        dicts = csv.DictReader(csv_data, delimiter="\t")
        if not dicts.fieldnames:
            raise KNWError(f"Could not get fieldnames for file: {file.name}")

        # remove silly characters from column names
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
    try:
        proc.process(blob)
    except (SQLAlchemyError, KNWError) as e:
        proc.logger.log(
            message=f"Unexpected Error while processing KNW data Full error: {str(e)}",
            severity=logging.ERROR,
        )
