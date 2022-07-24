from storage.postgres import create_psql_session


def test_create_psql_session(mocker):
    mock_engine, mock_session = mocker.MagicMock(), mocker.MagicMock()
    mock_create_engine = mocker.patch(
        "storage.postgres.create_engine", return_value=mock_engine
    )
    mock_sessionmaker = mocker.patch(
        "storage.postgres.sessionmaker", return_value=mock_session
    )

    result = create_psql_session("testuser", "testpw", "testhost")

    assert result == mock_session()
    mock_create_engine.assert_called_once_with(
        "postgresql://testuser:testpw@testhost:5432"
    )
    mock_sessionmaker.assert_called_once_with(bind=mock_engine)
