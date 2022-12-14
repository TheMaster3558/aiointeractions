"""
The MIT License (MIT)

Copyright (c) 2022-present The Master

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, Mapping, Optional, Set

import discord
from aiohttp import web
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

if discord.utils.HAS_ORJSON:
    from orjson import dumps, loads
else:
    from json import dumps, loads


__all__ = ('InteractionsApp',)


none_function: Callable[[Any], None] = lambda r: None
PONG: Dict[str, int] = {'type': 1}  # pong response


def get_latest_task(before_tasks: Set[asyncio.Task[Any]]) -> asyncio.Task[None]:
    return (asyncio.all_tasks() - before_tasks).pop()
    # guaranteed to be expected task because there are no awaits
    # inbetween calling this function and the all tasks get


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
    success_response: Callable[[web.Request], Any]
        A function (synchronous or asynchronous ) that accepts 1 argument,
        `request <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Request>`_
        that would return the body for the response.
    forbidden_response: Callable[[web.Request], Any]
        A function (synchronous or asynchronous ) that accepts 1 argument,
        `request <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Request>`_
        that would return the body for the response.


    .. warning::

        If the return value of `success_response` or `forbidden_response` are meant to be a JSON response, make sure to
        serialize the object to JSON format with `json.dumps <https://docs.python.org/3/library/json.html#json.dumps>`_.


    .. note::

        You can use `discord.utils.setup_logging() <https://discordpy.readthedocs.io/en/stable/api.html#discord.utils.setup_logging>`_
        for basic logging. Use ``discord.utils.setup_logging(root=False)`` to disable logging for `aiohttp`.
    """

    def __init__(
        self,
        client: discord.Client,
        *,
        app: Optional[web.Application] = None,
        route: str = '/interactions',
        success_response: Callable[[web.Request], Any] = none_function,
        forbidden_response: Callable[[web.Request], Any] = none_function,
    ) -> None:
        self.client: discord.Client = client
        self.verify_key: VerifyKey = discord.utils.MISSING

        if app is None:
            app = web.Application()

        app.add_routes([web.post(route, self.interactions_handler)])
        app.on_startup.append(self._set_running)
        app.on_shutdown.append(self._set_running)
        self.app: web.Application = app

        self.success_response: Callable[[web.Request], Any] = success_response
        self.forbidden_response: Callable[[web.Request], Any] = forbidden_response

        self._running: bool = False

    async def _set_running(self, _: Any) -> None:
        self._running = not self._running

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

    def is_running(self) -> bool:
        """
        Returns
        -------
        ``True`` if the app is running, otherwise ``False``.


        .. versionadded:: 1.1
        """
        return self._running

    async def interactions_handler(self, request: web.Request) -> web.Response:
        self.client.dispatch('interaction_request', request)
        body = await request.text()

        if not self._verify_request(request.headers, body):
            response = await discord.utils.maybe_coroutine(self.forbidden_response, request)
            return web.Response(status=401, body=response)

        self.client.dispatch('verified_interaction_request', request)
        data = loads(body)
        if data['type'] == 1:  # ping
            return web.Response(body=dumps(PONG))

        tasks = asyncio.all_tasks()
        self.client._connection.parse_interaction_create(data)
        await get_latest_task(tasks)

        response = await discord.utils.maybe_coroutine(self.success_response, request)
        return web.Response(status=200, body=response)

    async def start(self, token: str, **kwargs: Any) -> None:
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
        await web._run_app(self.app, **kwargs)
