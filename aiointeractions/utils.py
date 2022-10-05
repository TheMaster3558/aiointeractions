import logging
from typing import Any

import discord.utils


__all__ = ('setup_logging',)


MISSING = discord.utils.MISSING


def setup_logging(
    handler: logging.Handler = MISSING,
    formatter: logging.Formatter = MISSING,
    level: int = MISSING,
) -> None:
    """
    A function to help setup logging that is similar to discord.py's
    `setup_logging <https://discordpy.readthedocs.io/en/latest/api.html#discord.utils.setup_logging>`_ but for this library instead.

    Parameters
    ----------
    handler: :class:`logging.Handler`
        The log handler to use for the library's logger.
        The default log handler if not provided is :class:`logging.StreamHandler`.
    formatter: :class:`logging.Formatter`
        The formatter to use with the given log handler. Defaults to a colour based logging formatter if possible.
    level: :class:`int`
        The default log level for the library's logger. Defaults to ``logging.INFO``.
    """
    if handler is MISSING:
        handler = logging.StreamHandler()

    if formatter is MISSING:
        if isinstance(handler, logging.StreamHandler) and discord.utils.stream_supports_colour(handler.stream):
            formatter = discord.utils._ColourFormatter()
        else:
            dt_fmt = '%Y-%m-%d %H:%M:%S'
            formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

    if level is MISSING:
        level = logging.INFO

    handler.setFormatter(formatter)
    logger = logging.getLogger('aiointeractions')
    logger.setLevel(level)
    logger.addHandler(handler)


def _separate() -> str:
    return '\n' + '-' * 200


if discord.utils.HAS_ORJSON:
    from orjson import loads as _loads
else:
    from json import loads as _loads
