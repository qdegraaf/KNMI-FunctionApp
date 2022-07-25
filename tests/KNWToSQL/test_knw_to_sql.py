from datetime import datetime

import pytest
from sqlalchemy.exc import SQLAlchemyError

from KNWToSQL.errors import KNWError


def test_process_raises_error_and_calls_rollback_on_sqlalchemy_error(
    mock_row, mock_processor, mock_input_stream, mocker
):
    mocker.patch(
        "KNWToSQL.knw_to_sql.Processor.read_file_into_dicts",
        return_value=[mock_row, mock_row],
    )
    mock_processor.sql_session.commit.side_effect = SQLAlchemyError("oops")
    with pytest.raises(SQLAlchemyError) as excinfo:
        mock_processor.process(mock_input_stream)
    mock_processor.sql_session.add.call_count = 2
    mock_processor.sql_session.commit.assert_called_once()

    mock_processor.logger.log.assert_called_with(
        message="Encountered unexpected SQLAlchemyError: oops", severity=40
    )
    assert str(excinfo.value) == "oops"


def test_process_adds_rows_to_sql_session_and_commits(
    mock_processor, mock_row, mock_input_stream, mocker
):
    mocker.patch(
        "KNWToSQL.knw_to_sql.Processor.read_file_into_dicts",
        return_value=[mock_row, mock_row],
    )

    mock_processor.process(mock_input_stream)

    mock_processor.sql_session.add.call_count = 2
    mock_processor.sql_session.commit.assert_called_once()
    last_add_call_args = mock_processor.sql_session.add.call_args_list[1][0][0]
    assert last_add_call_args.dtg == datetime(2022, 1, 1, 13)
    assert last_add_call_args.f010 == 1.2
    assert last_add_call_args.d010 == 2.2
    assert last_add_call_args.t010 == 3.2
    assert last_add_call_args.q010 == 4.2
    assert last_add_call_args.p010 == 3.2


def test_read_files_into_dicts_raises_error_if_no_fieldnames(
    mock_processor, mock_empty_input_stream
):
    with pytest.raises(KNWError) as excinfo:
        mock_processor.read_file_into_dicts(mock_empty_input_stream)

    assert str(excinfo.value) == "Could not get fieldnames for file: knw.csv"


def test_read_files_into_dicts_returns_list_of_dicts(mock_processor, mock_input_stream):
    result = mock_processor.read_file_into_dicts(mock_input_stream)

    assert len(result) == 94

    assert result[0]["DTG"] == "1979-01-01 01:00"
    assert result[0]["F010"] == "5.77"
    assert result[0]["D010"] == "30.98"
    assert result[0]["T010"] == "270.16"
    assert result[0]["Q010"] == "0.002261"
    assert result[0]["P010"] == "100552.5"
