Frequently Asked Questions
==========================

What is the point of using this?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You don't need to connect to the gateway if you only want interactions.

Why are some interaction attributes ``None``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The bot will not be connected to the gateway so the cache will not be filled.
You can use your bot instance's fetch methods to get an object if needed.

What route does the app receive interactions in?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``/interactions``

Can I still use message commands?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The bot will not receive message events because it is not connected to
the gateway so you cannot use message commands.
