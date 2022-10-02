import asyncio
from json import loads
from typing import Any, Mapping, Optional

import discord
from aiohttp import web
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError


__all__ = ('InteractionsApp',)


class InteractionsApp:
    """A web application made with `aiohttp` for receiving aiointeractions from Discord.

    Parameters
    -----------
    client: :class:`discord.Client`
        The discord.py client instance for the web application to use.
    app: Optional[:class:`aiohttp.web.Application`]
        A pre-existing web application to add the aiointeractions route to.
        If not passed, a new web application instance will be created.
    """
    def __init__(self, client: discord.Client, *, app: Optional[web.Application] = None) -> None:
        self.verify_key: VerifyKey = discord.utils.MISSING

        if app is None:
            app = web.Application()
            app.cleanup = self._cleanup

        self.app = app
        self.app.add_routes(
            [
                web.post('/aiointeractions', self.interactions_endpoint)
            ]
        )

        self.client = client

    def _validate_request(self, headers: Mapping[str, Any], body: str) -> bool:
        signature = headers['X-Signature-Ed25519']
        timestamp = headers['X-Signature-Timestamp']

        try:
            self.verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        except BadSignatureError:
            return False
        return True

    async def _cleanup(self) -> None:
        await self.client.close()

    async def interactions_endpoint(self, request: web.Request) -> web.Response:
        body = await request.text()
        if not self._validate_request(request.headers, body):
            return web.Response(status=401)

        data = loads(body)
        if data['type'] == discord.InteractionType.ping:
            return web.json_response(
                {
                    'type': discord.InteractionResponseType.pong
                }
            )

        self.client._connection.parse_interaction_create(data)
        await asyncio.sleep(3)
        return web.Response(status=204)

    async def start(self, token: str, **kwargs: Any) -> None:
        """
        Start the web server and call the `login method https://discordpy.readthedocs.io/en/latest/api.html#discord.Client.login`_.

        Parameters
        -----------
        token: :class:`str`
            The authentication token.
        **kwargs:
            The :term:`keyword argument`s to pass onto `aiohttp.web.run_app https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.run_app`_.

        .. note::

            You can `asyncio.run https://docs.python.org/3/library/asyncio-task.html#asyncio.run`_ to call this method
            from synchronous context.

        .. warning::

            You are responsible for closing your bot instance. This library will not do it for you.
        """
        await self.client.login(token)
        assert self.client.application is not None

        self.verify_key = VerifyKey(bytes.fromhex(self.client.application.verify_key))
        await web._run_app(self.app, **kwargs)
