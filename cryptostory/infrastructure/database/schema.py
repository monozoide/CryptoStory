import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.types import Enum as EnumType
from cryptostory.domain.value_objects import Interval
from cryptostory.domain.models import JobStatus

metadata = sa.MetaData()
candles_table = sa.Table(
    "candles",
    metadata,
    sa.Column("symbol", sa.String(20), primary_key=True),
    sa.Column("interval", EnumType(Interval, name="interval_enum"), primary_key=True),
    sa.Column("open_time", sa.DateTime(timezone=True), primary_key=True),
    sa.Column("open", sa.Numeric(20, 10)),
    sa.Column("high", sa.Numeric(20, 10)),
    sa.Column("low", sa.Numeric(20, 10)),
    sa.Column("close", sa.Numeric(20, 10)),
    sa.Column("volume", sa.Numeric(30, 10)),
    sa.Column("close_time", sa.DateTime(timezone=True)),
    sa.Column("quote_asset_volume", sa.Numeric(30, 10)),
    sa.Column("number_of_trades", sa.Integer),
    sa.Column("taker_buy_base_asset_volume", sa.Numeric(30, 10)),
    sa.Column("taker_buy_quote_asset_volume", sa.Numeric(30, 10)),
)
configured_symbols_table = sa.Table(
    "configured_symbols",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("symbol", sa.String(20)),
    sa.Column("interval", EnumType(Interval, name="interval_enum")),
    sa.Column("is_active", sa.Boolean),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    sa.UniqueConstraint("symbol", "interval"),
)
fetch_jobs_table = sa.Table(
    "fetch_jobs",
    metadata,
    sa.Column("id", UUID(as_uuid=True), primary_key=True),
    sa.Column("symbol", sa.String(20)),
    sa.Column("interval", EnumType(Interval, name="interval_enum")),
    sa.Column("start_time", sa.DateTime(timezone=True)),
    sa.Column("end_time", sa.DateTime(timezone=True)),
    sa.Column("status", EnumType(JobStatus, name="job_status_enum")),
    sa.Column("logs", JSONB),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
)
