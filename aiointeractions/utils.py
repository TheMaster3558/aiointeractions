import logging
from typing import Optional

import discord.utils


__all__ = ('setup_logging',)


MISSING = discord.utils.MISSING


def setup_logging(
    handler: Optional[logging.Handler] = MISSING,
    formatter: logging.Formatter = MISSING,
    level: int = MISSING,
):
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
