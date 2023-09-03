Migrating to v2
===============

.. currentmodule:: aiointeractions

Deprecation of :meth:`InteractionsApp.start()`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``start()`` method is being removed in favor of aiohttp's asynchronous start methods.
The reason behind this is the ``start()`` method uses ``aiohttp.web._run_app()`` which is a private method
so it's best to move away from using undocumented methods.


.. tabs::

  .. group-tab:: Old

    .. code:: py

        import asyncio

        import aiointeractions
        from aiohttp import web

        client = discord.Client(...)
        app = aiointeractions.InteractionsApp(client, ...)

        async def main():
            async with client:
                await app.start('token')

        asyncio.run(main())


  .. group-tab:: New

    .. code:: py

        import asyncio

        import aiointeractions
        from aiohttp import web

        client = discord.Client(...)
        app = aiointeractions.InteractionsApp(client, ...)

        async def main():
            async with client:
                await app.setup('token')
                # if you would like to call setup() after the web server is started like app.run()
                # do this instead of await app.setup('token')
                #
                # import functools
                # app.app.on_startup.append(functools.partial(app.setup, 'token'))

                runner = web.AppRunner(app.aiohttp_app)
                await runner.setup()
                site = web.TCPSite(runner)
                await site.start()

                try:
                    while True:
                        await asyncio.sleep(3600)
                finally:
                    await runner.cleanup()

        asyncio.run(main())


Addition of :meth:`InteractionsApp.setup()`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This new method logs in the discord client and fetches verification keys.
This method is automatically called in :meth:`InteractionsApp.run()` so only use it if you are using alternative start methods
such as the method above.


Removal of the ``raise_for_bad_response`` parameter for :class:`InteractionsApp`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Now ``aiohttp.web.HTTPUnauthorized`` will always be raised for invalid authentication.



Rename ``InteractionsApp.app`` to ``aiohttp_app``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Both the parameter ``app`` for the constructor of :class:`InteractionsApp` and the attribute ``app`` have been renamed to ``aiohttp_app``.
The goal of this is to add distinction in scenarios such as this.

.. code:: py

    app = aiointeractions.InteractionsApp()
    print('The aiohttp app is', app.app)
                                ^^^^^^^


Other changes to :class:`InteractionsApp`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- The discord client login and the fetching of the verification keys from :meth:`InteractionsApp.setup()` now are called after the web server is started, instead of before.
