import argparse
import asyncio
from .services.fetch_service import FetchService
from .adapters.binance_client import BinanceClient
from .infrastructure.database.repositories.candle_repository import CandleRepository
from .infrastructure.database.session import AsyncSessionLocal
from .domain.models import ConfiguredSymbol
from .domain.value_objects import Interval
from .services.rate_limiter import RateLimiter


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol")
    parser.add_argument("interval")
    args = parser.parse_args()
    async with AsyncSessionLocal() as session:
        service = FetchService(
            BinanceClient(), CandleRepository(session), RateLimiter(1200)
        )
        await service.fetch_and_store(
            ConfiguredSymbol(symbol=args.symbol, interval=Interval(args.interval))
        )


if __name__ == "__main__":
    asyncio.run(main())
