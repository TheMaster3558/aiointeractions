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
import warnings
from typing import Any, AsyncGenerator, Callable, Mapping, Optional, Set

import discord
from aiohttp import web
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

if discord.utils.HAS_ORJSON:  # pragma: no cover
    from orjson import dumps, loads
else:
    from json import dumps, loads


__all__ = ('InteractionsApp',)


# create a prettier repr for the docs, <function <lambda>> -> <do_nothing>
try:  # pragma: no cover
    if __sphinx_build__:  # type: ignore # defined in docs/conf.py

        class DoNothing:
            def __repr__(self) -> str:
                return "<do_nothing>"

        none_function = DoNothing()  # type: ignore
    else:
        none_function: Callable[[Any], None] = lambda r: None
except NameError:
    none_function: Callable[[Any], None] = lambda r: None


PONG: web.Response
data = dumps({'type': 1})
if isinstance(data, bytes):  # pragma: no cover
    PONG = web.Response(status=200, body=data)
elif isinstance(data, str):
    PONG = web.Response(status=200, text=data)
else:  # pragma: no cover
    assert False


def get_latest_task(before_tasks: Set[asyncio.Task[Any]]) -> asyncio.Task[Any]:
    return (asyncio.all_tasks() - before_tasks).pop()
    # guaranteed to be expected task because there are no awaits
    # inbetween calling this function and the all tasks get


class InteractionsApp:
    """A web application made with `aiohttp` for receiving interactions from Discord.

    Parameters
    ----------
    client: :class:`discord.Client`
        The discord.py client instance for the web application to use. This can be :class:`discord.Client`
        or any subclass of it such as :class:`discord.ext.commands.Bot`
    app: Optional[:class:`aiohttp.web.Application`]
        A pre-existing web application to add the interactions route to.
        If not passed, a new web application instance will be created.
    route: :class:`str`
        The route to add the interactions handler to. Defaults to ``/interactions``.
    success_response: Callable[[web.Request], Any]
        A function (synchronous or asynchronous) that accepts 1 argument,
        `request <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Request>`_
        that would return the body for the response. Defaults to a function that would do nothing.
    forbidden_response: Callable[[web.Request], Any]
        A function (synchronous or asynchronous) that accepts 1 argument,
        `request <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Request>`_
        that would return the body for the response. Defaults to a function that would do nothing.
    raise_for_bad_response: :class:`bool`
        Whether to raise `aiohttp.web.HTTPException <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.HTTPException>`_
        on a bad request, if ``False`` returns `aiohttp.web.Response <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Response>`_
        This parameter will always be ``True`` starting from v2.

        .. versionadded:: 1.2


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
        raise_for_bad_response: bool = False,
    ) -> None:
        self.client: discord.Client = client
        self.verify_key: VerifyKey = discord.utils.MISSING

        if app is None:
            app = web.Application()

        app.add_routes([web.post(route, self.interactions_handler)])
        app.cleanup_ctx.append(self._set_running)
        self.app: web.Application = app

        self.success_response: Callable[[web.Request], Any] = success_response
        self.forbidden_response: Callable[[web.Request], Any] = forbidden_response
        self.raise_for_bad_response: bool = raise_for_bad_response

        self._running: bool = False

    async def _set_running(self, app: web.Application) -> AsyncGenerator[None, None]:
        self._running = True

        yield

        self._running = False

    def _verify_request(self, headers: Mapping[str, Any], body: str) -> bool:  # pragma: no cover
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

    def _handle_unauthorized_request(self, body: Any) -> web.Response:
        if self.raise_for_bad_response:
            raise web.HTTPUnauthorized(body=body)
        return web.Response(status=401, body=body)

    async def interactions_handler(self, request: web.Request) -> web.Response:
        self.client.dispatch('interaction_request', request)
        body = await request.text()

        if not self._verify_request(request.headers, body):
            response = await discord.utils.maybe_coroutine(self.forbidden_response, request)
            return self._handle_unauthorized_request(response)

        self.client.dispatch('verified_interaction_request', request)
        data = loads(body)
        if data['type'] == 1:  # ping
            return PONG

        tasks = asyncio.all_tasks()
        self.client._connection.parse_interaction_create(data)
        await get_latest_task(tasks)

        response = await discord.utils.maybe_coroutine(self.success_response, request)
        return web.Response(status=200, body=response)

    def _set_verify_key(self, verify_key: str) -> None:  # pragma: no cover
        self.verify_key = VerifyKey(bytes.fromhex(verify_key))

    async def setup(self, token: str) -> web.Application:  # pragma: no cover
        """
        Setup the discord client by logging in and fetching the servers verification keys.
        Call this method if you are using aiohttp's asynchronous startup instead of :meth:`run()`

        Parameters
        ----------
        token: :class:`str`
            The authentication token.


        .. versionadded:: 2.0
        """
        await self.client.login(token)
        assert self.client.application is not None

        self._set_verify_key(self.client.application.verify_key)
        return self.app

    async def start(self, token: str, **kwargs: Any) -> None:  # pragma: no cover
        """
        Start the web server and call the `login method <https://discordpy.readthedocs.io/en/latest/api.html#discord.Client.login>`_.
        This method gives more control over initialization and cleanup than :meth:`run()`.

        Parameters
        ----------
        token: :class:`str`
            The authentication token for discord.
        \*\*kwargs
            The keyword arguments to pass onto `aiohttp.web.run_app <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.run_app>`_.


        .. warning::

            When using this method, this library will not handle discord client cleanup, event loop cleanup, nor provide a graceful shutdown.
            It is recommended to use :meth:`run()` instead for simplicity.


        .. deprecated:: 2.0

            :meth:`start()` will be removed in v2.2. Use aiohttp's asynchronous startup instead.
            Below is an alternative.

            .. code:: py

                import asyncio

                import aiointeractions
                from aiohttp import web

                client = discord.Client(...)
                app = aiointeractions.InteractionsApp(client, ...)

                async def main():
                    async with client:
                        await app.setup('token')

                        runner = web.AppRunner(app.app)
                        await runner.setup()
                        site = web.TCPSite(runner)
                        await site.start()

                        try:
                            while True:
                                await asyncio.sleep(3600)
                        finally:
                            await runner.cleanup()

                asyncio.run(main())

        """
        warnings.warn(
            'start() will be removed in version 2.2 in favor of using aiohttp\'s own asynchronous startup methods',
            category=DeprecationWarning,
        )
        await web._run_app(self.setup(token), **kwargs)

    def run(self, token: str, **kwargs: Any) -> None:  # pragma: no cover
        """
        A top-level blocking call that automatically handles cleanup for the discord client, event loop, and provides a graceful shutdown.
        This automatically calls :meth:`setup()`.

        Parameters
        ----------
        token: :class:`str`
            The authentication token for discord.
        \*\*kwargs
            The keyword arguments to pass onto `aiohttp.web.run_app <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.run_app>`_.


        .. versionadded:: 1.3
        """
        self.app.on_cleanup.append(lambda _: self.client.close())
        web.run_app(self.setup(token), **kwargs)
