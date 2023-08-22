import discord
import pytest

import aiointeractions

intents = discord.Intents.none()
client = discord.Client(intents=intents)
app = aiointeractions.InteractionsApp(client)


@pytest.mark.asyncio
async def test_set_running() -> None:
    assert app.is_running() is False
    await app._set_running(discord.utils.MISSING).asend(None)
    assert app.is_running() is True
