"""Tests for SQLAlchemy schemas."""

from sqlalchemy import UniqueConstraint

from cryptostory.infrastructure.schemas import CandleModel, EventModel, FetchJobModel, SymbolModel


def test_symbol_model_table_name() -> None:
    assert SymbolModel.__tablename__ == "symbols"


def test_candle_model_table_name() -> None:
    assert CandleModel.__tablename__ == "candles"


def test_fetch_job_model_table_name() -> None:
    assert FetchJobModel.__tablename__ == "fetch_jobs"


def test_event_model_table_name() -> None:
    assert EventModel.__tablename__ == "events"


def test_candle_unique_constraint() -> None:
    constraints = [constraint for constraint in CandleModel.__table_args__ if isinstance(constraint, UniqueConstraint)]
    assert any(constraint.name == "uq_candles_symbol_interval_time" for constraint in constraints)
