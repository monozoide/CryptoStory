import time
import asyncio


class RateLimiter:
    def __init__(self, rate: int, period: int = 60):
        self.rate = rate
        self.period = period
        self.tokens = rate
        self.updated_at = time.monotonic()

    async def acquire(self):
        while self.tokens < 1:
            await asyncio.sleep(0.1)
        now = time.monotonic()
        self.tokens += (now - self.updated_at) * self.rate / self.period
        self.updated_at = now
        self.tokens = min(self.rate, self.tokens)
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
