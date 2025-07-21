aiointeractions
===============

An async Discord HTTP Interactions wrapper for `discord.py` built with `aiohttp`.


⚠️ **Warning:** This library is no longer compatible with ``discord.py>2.4`` due to changes in how interactions are parsed


.. image:: /docs/_static/logo.png
  :alt: The aiointeractions logo


Documentation
-------------
https://aiointeractions.readthedocs.io/


Installing
----------
`aiointeractions` requires Python 3.8 or newer.

.. code::

    pip install aiointeractions


Example
-------

.. code:: py

    import asyncio
    import discord
    import aiointeractions

    intents = discord.Intents.none()
    # intents are not required because there is no gateway connection

    client = discord.Client(intents=intents)
    tree = discord.app_commands.CommandTree(client)
    app = aiointeractions.InteractionsApp(client)

    discord.utils.setup_logging(root=True)

    @tree.command()
    async def ping(interaction: discord.Interaction) -> None:
        await interaction.response.send_message('Pong!')

    app.run('bot token')


Fork Support
------------
While some forks may be compatible, discord.py forks will not be supported.
