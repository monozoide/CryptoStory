"""Initial schema for CryptoStory."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "symbols",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("symbol", sa.String(length=32), nullable=False, unique=True),
        sa.Column("exchange", sa.Enum("binance", name="exchange_type"), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.String(length=128), nullable=False, server_default="system"),
    )

    op.create_table(
        "candles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("symbol", sa.String(length=32), sa.ForeignKey("symbols.symbol"), nullable=False),
        sa.Column("interval", sa.Enum("1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M", name="interval"), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Float, nullable=False),
        sa.Column("high", sa.Float, nullable=False),
        sa.Column("low", sa.Float, nullable=False),
        sa.Column("close", sa.Float, nullable=False),
        sa.Column("volume", sa.Float, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.String(length=128), nullable=False, server_default="system"),
        sa.UniqueConstraint("symbol", "interval", "time", name="uq_candles_symbol_interval_time"),
    )

    op.create_table(
        "fetch_jobs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("symbol", sa.String(length=32), sa.ForeignKey("symbols.symbol"), nullable=False),
        sa.Column("interval", sa.Enum("1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M", name="interval"), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.String(length=128), nullable=False, server_default="system"),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("symbol", sa.String(length=32), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.String(length=128), nullable=False, server_default="system"),
    )

    op.execute(
        """
        SELECT create_hypertable('candles', 'time', 'symbol', 8, if_not_exists => TRUE);
        """
    )
    op.execute(
        """
        ALTER TABLE candles SET (timescaledb.compress, timescaledb.compress_segmentby = 'symbol');
        """
    )
    op.execute("SELECT add_compression_policy('candles', INTERVAL '30 days');")


def downgrade() -> None:
    op.execute("SELECT remove_compression_policy('candles');")
    op.execute("DROP TABLE IF EXISTS events;")
    op.execute("DROP TABLE IF EXISTS fetch_jobs;")
    op.execute("DROP TABLE IF EXISTS candles;")
    op.execute("DROP TABLE IF EXISTS symbols;")
    op.execute("DROP TYPE IF EXISTS interval;")
    op.execute("DROP TYPE IF EXISTS exchange_type;")
