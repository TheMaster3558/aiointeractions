import asyncio
import logging
import json
from typing import Any, Dict, Mapping, Optional

import discord
from aiohttp import web
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from .utils import _separate


__all__ = ('InteractionsApp',)


log = logging.getLogger('aiointeractions')

MISSING = discord.utils.MISSING

PING: int = discord.InteractionType.ping.value
PONG: Dict[str, int] = {'type': discord.InteractionResponseType.pong.value}


class InteractionsApp:
    """A web application made with `aiohttp` for receiving interactions from Discord.

    Parameters
    ----------
    client: :class:`discord.Client`
        The discord.py client instance for the web application to use.
    app: Optional[:class:`aiohttp.web.Application`]
        A pre-existing web application to add the `/interactions` route to.
        If not passed, a new web application instance will be created.
    """

    def __init__(self, client: discord.Client, *, app: Optional[web.Application] = None) -> None:
        self.verify_key: VerifyKey = MISSING

        if app is None:
            app = web.Application()
            app.cleanup = self._cleanup

        app.add_routes([web.post('/interactions', self.interactions_endpoint)])
        self.app = app

        self.client = client

    def _verify_request(self, headers: Mapping[str, Any], body: str) -> bool:
        signature = headers.get('X-Signature-Ed25519')
        timestamp = headers.get('X-Signature-Timestamp')
        log.debug('Signature: %s, Timestamp: %s', signature, timestamp)

        if not signature or not timestamp:
            return False
        try:
            self.verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        except BadSignatureError:
            return False
        return True

    async def _cleanup(self) -> None:
        await self.client.close()

    async def interactions_endpoint(self, request: web.Request) -> web.Response:
        body = await request.text()
        log.debug('Received request, verifying...')

        if not self._verify_request(request.headers, body):
            log.debug('Verification failed, responding with 401.' + _separate())
            return web.Response(status=401)
        log.debug('Verification success')

        data = json.loads(body)
        log.debug('Decoded request data: %s', data)

        if data['type'] == PING:
            return web.json_response(PONG)

        log.debug('Passing interaction data to client instance' + _separate())
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
        log.info('Starting web application')
        await web._run_app(self.app, **kwargs)
