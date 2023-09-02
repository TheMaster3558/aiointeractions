import asyncio
import json
from typing import Any, MutableMapping, Tuple

import discord
import pytest
from discord import app_commands

import aiointeractions

with open('tests/mock_interaction.json', 'r') as f:
    data = json.load(f)


class MockApp(aiointeractions.InteractionsApp):
    verification: Tuple[str, ...] = (json.dumps({'type': 1}), json.dumps(data))

    def _verify_request(self, headers: MutableMapping[str, Any], body: str) -> bool:
        return str(body) in self.verification


@pytest.mark.asyncio
async def test_no_verification(aiohttp_client) -> None:
    intents = discord.Intents.none()
    discord_client = discord.Client(intents=intents)
    app = MockApp(discord_client)

    client = await aiohttp_client(app.aiohttp_app)
    response = await client.post('/interactions', headers={}, data='')

    assert response.status == 401


@pytest.mark.asyncio
async def test_invalid_verification_exception(aiohttp_client) -> None:
    intents = discord.Intents.none()
    discord_client = discord.Client(intents=intents)
    app = MockApp(discord_client)

    client = await aiohttp_client(app.aiohttp_app)
    response = await client.post('/interactions', headers={}, data='badtext')

    assert response.status == 401


@pytest.mark.asyncio
async def test_valid_verification_ping(aiohttp_client) -> None:
    intents = discord.Intents.none()
    discord_client = discord.Client(intents=intents)
    app = MockApp(discord_client)

    client = await aiohttp_client(app.aiohttp_app)
    response = await client.post('/interactions', headers={}, json={'type': 1})

    assert response.status == 200 and json.loads(await response.text())['type'] == 1


@pytest.mark.asyncio
async def test_command(aiohttp_client) -> None:
    intents = discord.Intents.none()
    discord_client = discord.Client(intents=intents)
    discord_client.loop = asyncio.get_running_loop()

    app = MockApp(discord_client)
    tree = app_commands.CommandTree(discord_client)

    changed = False

    @tree.command()
    async def test_command(interaction: discord.Interaction) -> None:
        nonlocal changed
        changed = True

    client = await aiohttp_client(app.aiohttp_app)
    await client.post('/interactions', headers={}, json=data)

    assert changed is True


@pytest.mark.asyncio
async def test_success_response(aiohttp_client) -> None:
    intents = discord.Intents.none()
    discord_client = discord.Client(intents=intents)
    discord_client.loop = asyncio.get_running_loop()

    app = MockApp(discord_client, success_response=lambda r: 'The Master is cool')
    tree = app_commands.CommandTree(discord_client)

    @tree.command()
    async def test_command(interaction: discord.Interaction) -> None:
        ...

    client = await aiohttp_client(app.aiohttp_app)
    response = await client.post('/interactions', headers={}, json=data)

    assert response.status == 200 and await response.text() == 'The Master is cool'
