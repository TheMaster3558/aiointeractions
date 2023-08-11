API Reference
=============

.. automodule:: aiointeractions
  :members:


Event Reference
~~~~~~~~~~~~~~~
.. currentmodule:: None

You can listen to the following events on your client instance.

.. function:: on_interaction_request(request)

    Called when a request to the interactions endpoint has been received.
    The interaction has not been verified yet so it can be from anywhere.

    :param request: The request object.
    :type request: `aiohttp.web.Request <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Request>`_

    .. note:: The request may not be an interaction, it may be a ping from Discord.


.. function:: on_verified_interaction_request(request)

    Called when a request to the interactions endpoint has been received
    and it has been verified.

    The parameters are the same as :func:`on_interaction_request`.
