Frequently Asked Questions
==========================

What is the point of using this?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You don't need to connect to the gateway if you only want interactions.

Why are some interaction attributes ``None``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The bot will not be connected to the gateway so the cache will not be filled.
You can use your bot instance's fetch methods to get an object if needed.

Can I still use message commands?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The bot will not receive message events because it is not connected to
the gateway so you cannot use message commands.

How do I set the interactions endpoint?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Open the Discord Developer Portal.
2. Navigate to the **General Information** page in your chosen application.
3. Now find **Interactions Endpoint URL** and set the url. Make sure it ends with ``/interactions``.

Why isn't ``on_ready`` firing?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``on_ready`` is fired when the cache is ready but since the bot is
not connected to the gateway it will never be ready. Consider using ``setup_hook`` instead.
