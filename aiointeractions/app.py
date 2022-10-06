import asyncio
from typing import Any, Dict, Mapping, Optional

import discord
from aiohttp import web
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

if discord.utils.HAS_ORJSON:
    from orjson import loads
else:
    from json import loads


__all__ = ('InteractionsApp',)


MISSING = discord.utils.MISSING
PONG: Dict[str, int] = {'type': 1}  # pong response


class InteractionsApp:
    """A web application made with `aiohttp` for receiving interactions from Discord.

    Parameters
    ----------
    client: :class:`discord.Client`
        The discord.py client instance for the web application to use.
    app: Optional[:class:`aiohttp.web.Application`]
        A pre-existing web application to add the interactions route to.
        If not passed, a new web application instance will be created.
    route: :class:`str`
        The route to add the interactions handler to. Defaults to ``/interactions``.
    """

    def __init__(
            self,
            client: discord.Client,
            *,
            app: Optional[web.Application] = None,
            route: str = '/interactions'
    ) -> None:
        self.client = client
        self.verify_key: VerifyKey = MISSING

        if app is None:
            app = web.Application()

        app.add_routes([web.post(route, self.interactions_handler)])
        self.app: web.Application = app

        self._runner_task: Optional[asyncio.Task[None]] = None

    def _verify_request(self, headers: Mapping[str, Any], body: str) -> bool:
        signature = headers.get('X-Signature-Ed25519')
        timestamp = headers.get('X-Signature-Timestamp')

        if not signature or not timestamp:
            return False
        try:
            self.verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        except BadSignatureError:
            return False
        return True

    async def interactions_handler(self, request: web.Request) -> web.Response:
        self.client.dispatch('interaction_request', request)
        body = await request.text()

        if not self._verify_request(request.headers, body):
            return web.Response(status=401)

        self.client.dispatch('verified_interaction_request', request)
        data = loads(body)
        if data['type'] == 1:  # ping
            return web.json_response(PONG)

        self.client._connection.parse_interaction_create(data)
        await asyncio.sleep(3)
        return web.Response(status=204)

    async def start(
            self,
            token: str,
            **kwargs: Any
    ) -> None:
        """
        Start the web server and call the `login method <https://discordpy.readthedocs.io/en/latest/api.html#discord.Client.login>`_.

        Parameters
        ----------
        token: :class:`str`
            The authentication token.
        \*\*kwargs
            The keyword arguments to pass onto `aiohttp.web.run_app <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.run_app>`_.


        .. warning::

            You are responsible for closing your bot instance. This library will not do it for you.
        """
        await self.client.login(token)
        assert self.client.application is not None

        self.verify_key = VerifyKey(bytes.fromhex(self.client.application.verify_key))
        self._runner_task = asyncio.create_task(web._run_app(self.app, **kwargs))
        await self._runner_task

    def close(self) -> None:
        """
        Close the app. If the app is not running then nothing will happen.
        """
        if self._runner_task is not None:
            self._runner_task.cancel()
