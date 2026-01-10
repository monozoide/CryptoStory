"""Repository test fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from unittest.mock import AsyncMock

import pytest


@dataclass
class FakeResult:
    items: list

    def scalar_one_or_none(self):
        return self.items[0] if self.items else None

    def scalars(self):
        return self

    def all(self) -> list:
        return self.items


@pytest.fixture()
def async_session() -> AsyncMock:
    session = AsyncMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.add = AsyncMock()
    return session


def fake_result(items: Iterable) -> FakeResult:
    return FakeResult(list(items))
