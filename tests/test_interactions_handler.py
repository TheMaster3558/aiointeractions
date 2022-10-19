from typing import Any, Mapping

import pytest

import aiointeractions
import discord


class MockRequest:
    def __init__(
            self,
            headers: Mapping[str, Any],
            data: Any
    ):
        self.headers = headers
        self._data = data

    async def text(self) -> str:
        return str(self._data)


class MockApp(aiointeractions.InteractionsApp):
    verification: str = '{}{"type": 1}'

    def _verify_request(self, headers: Mapping[str, Any], body: str) -> bool:
        return f'{headers}{body}' == self.verification


intents = discord.Intents.none()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

app = MockApp(client)


@pytest.mark.asyncio
async def test_no_verification() -> None:
    request = MockRequest({}, '')
    response = await app.interactions_handler(request)  # type: ignore
    assert response.status == 401


@pytest.mark.asyncio
async def test_invalid_verification() -> None:
    request = MockRequest({}, 'badtext')
    response = await app.interactions_handler(request)  # type: ignore
    assert response.status == 401


@pytest.mark.asyncio
async def test_valid_verification() -> None:
    request = MockRequest({}, '{"type": 1}')
    response = await app.interactions_handler(request)  # type: ignore
    assert response.status == 200
