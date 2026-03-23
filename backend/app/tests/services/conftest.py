"""LLM service tests are pure unit tests and skip the DB session autouse fixture."""

from collections.abc import Generator

import pytest


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[None, None, None]:
    yield
