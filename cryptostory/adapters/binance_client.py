import httpx
import datetime
from typing import List, Dict, Any


class BinanceAPIError(Exception):
    pass


class BinanceClient:
    def __init__(self, base_url: str = "https://api.binance.com"):
        self.client = httpx.AsyncClient(base_url=base_url)

    async def get_ui_klines(
        self, symbol: str, interval: str, **kwargs
    ) -> List[Dict[str, Any]]:
        params = {"symbol": symbol, "interval": interval, **kwargs}
        try:
            resp = await self.client.get("/api/v3/uiKlines", params=params)
            resp.raise_for_status()
            return [
                {
                    "open_time": datetime.datetime.fromtimestamp(
                        k[0] / 1000, tz=datetime.timezone.utc
                    ),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "close_time": datetime.datetime.fromtimestamp(
                        k[6] / 1000, tz=datetime.timezone.utc
                    ),
                    "quote_asset_volume": float(k[7]),
                    "number_of_trades": int(k[8]),
                    "taker_buy_base_asset_volume": float(k[9]),
                    "taker_buy_quote_asset_volume": float(k[10]),
                }
                for k in resp.json()
            ]
        except (httpx.HTTPError, ValueError) as e:
            raise BinanceAPIError from e
