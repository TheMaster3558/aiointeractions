Migrating to v2
===============

Deprecation of :meth:`InteractionsApp.start()`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The start() method is being removed in favor of aiohttp's asynchronous start methods.
The reason behind this is the start() method uses ``aiohttp.web._run_app()`` which is a private method
so it's best to move away from using undocumented methods.

**Old**

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


**New**

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
