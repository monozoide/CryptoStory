from .rate_limiter import RateLimiter
from ..adapters.binance_client import BinanceClient
from ..infrastructure.database.repositories.candle_repository import CandleRepository
from ..domain.models import ConfiguredSymbol, Candle


class FetchService:
    def __init__(
        self, client: BinanceClient, repo: CandleRepository, limiter: RateLimiter
    ):
        self.client = client
        self.repo = repo
        self.limiter = limiter

    async def fetch_and_store(self, config: ConfiguredSymbol):
        await self.limiter.acquire()
        klines = await self.client.get_ui_klines(
            config.symbol, config.interval.value, limit=1000
        )
        candles = [
            Candle(symbol=config.symbol, interval=config.interval, **k) for k in klines
        ]
        await self.repo.bulk_upsert(candles)
