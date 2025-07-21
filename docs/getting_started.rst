Getting Started
===============

Python Requirements
-------------------
Python 3.8 or newer is required.


Dependencies
------------
The only dependency is `discord.py`. However, `discord.py` versions from `v2.4` are no longer compatible with the library.


Installing
----------


.. tabs::

  .. group-tab:: Linux/MacOS

    .. code:: shell

        $ python -m pip install -U aiointeractions

  .. group-tab:: Windows

    .. code:: shell

        $ py -m pip install -U aiointeractions


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
