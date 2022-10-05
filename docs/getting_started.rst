Getting Started
===============

Python Requirements
-------------------
Python 3.8 or newer is required.


Dependencies
------------
The only dependency is `discord.py`


Installing
----------

.. code:: shell

    $ pip install aiointeractions


Example
-------

.. code:: py

    import asyncio
    import discord
    import aiointeractions

    intents = discord.Intents.none()
    # intents are not required because there is no gateway conenction

    client = discord.Client(intents=intents)
    tree = discord.app_commands.CommandTree(client)
    app = aiointeractions.InteractionsApp(client)

    @tree.command()
    async def ping(interaction: discord.Interaction) -> None:
        await interaction.response.send_message('Pong!')

    async def main():
        async with client:
            await app.start()
            # your bot will now receive interactions

    asyncio.run(main())


Fork Support
------------
While some forks may be compatible, discord.py forks will not be supported.
