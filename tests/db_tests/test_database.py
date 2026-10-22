from unittest.mock import MagicMock

import pytest
from sqlalchemy import MetaData
from sqlalchemy.orm import Session

from db import database
from db.database import SQLALCHEMY_DATABASE_URL, Base, SessionLocal, engine, get_db


def test_database_url_configured():
    """Verify that the database URL is configured for SQLite."""
    assert SQLALCHEMY_DATABASE_URL == "sqlite:///./app.db"
    assert SQLALCHEMY_DATABASE_URL.startswith("sqlite:///")


def test_engine_properties():
    """Verify that SQLAlchemy engine is instantiated with the SQLite dialect."""
    assert engine.dialect.name == "sqlite"
    assert engine.url.database == "./app.db"


def test_session_local_configuration():
    """Verify that SessionLocal creates valid sessions with autocommit and autoflush disabled."""
    assert SessionLocal.kw.get("autocommit") is False
    assert SessionLocal.kw.get("autoflush") is False

    session = SessionLocal()
    try:
        assert isinstance(session, Session)
        assert session.bind == engine
    finally:
        session.close()


def test_base_declarative_metadata():
    """Verify that Base is a declarative base having SQLAlchemy metadata."""
    assert hasattr(Base, "metadata")
    assert isinstance(Base.metadata, MetaData)


def test_get_db_yields_session_and_closes(monkeypatch):
    """Verify get_db generator yields a session and closes it on normal exit."""
    mock_session = MagicMock(spec=Session)
    mock_sessionmaker = MagicMock(return_value=mock_session)
    monkeypatch.setattr(database, "SessionLocal", mock_sessionmaker)

    gen = get_db()
    session = next(gen)
    assert session is mock_session
    mock_session.close.assert_not_called()

    with pytest.raises(StopIteration):
        next(gen)

    mock_session.close.assert_called_once()


def test_get_db_closes_session_on_exception(monkeypatch):
    """Verify get_db generator ensures the session is closed if an exception occurs."""
    mock_session = MagicMock(spec=Session)
    mock_sessionmaker = MagicMock(return_value=mock_session)
    monkeypatch.setattr(database, "SessionLocal", mock_sessionmaker)

    gen = get_db()
    session = next(gen)
    assert session is mock_session

    with pytest.raises(RuntimeError, match="DB operation error"):
        gen.throw(RuntimeError("DB operation error"))

    mock_session.close.assert_called_once()
