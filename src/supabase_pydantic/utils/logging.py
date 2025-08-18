from __future__ import annotations

import logging
import sys
from types import FrameType

try:
    from loguru import logger  # type: ignore

    _HAS_LOGURU = True
except Exception:  # pragma: no cover - fallback path
    logger = None  # type: ignore
    _HAS_LOGURU = False


class InterceptHandler(logging.Handler):
    """Redirect standard logging records to Loguru if available."""

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - trivial  # noqa: D102
        if not _HAS_LOGURU or logger is None:
            return
        level = record.levelno if isinstance(record.levelno, int) else logger.level(record.levelname).name

        # Compute correct depth by skipping frames from stdlib logging module
        frame: FrameType | None = logging.currentframe()
        depth = 2
        # Walk back until we leave the logging module
        while frame and frame.f_code.co_filename == getattr(logging, '__file__', None):
            frame = frame.f_back
            depth += 1

        logger.bind(logger_name=record.name).opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(debug: bool = False) -> None:
    """Configure Loguru if available; otherwise stdlib logging.

    Call once at CLI entry or command start.
    """
    level = logging.DEBUG if debug else logging.INFO

    if _HAS_LOGURU and logger is not None:
        # Remove existing handlers configured by other libs
        logging.root.handlers = []
        logging.root.setLevel(level)

        # Configure Loguru
        logger.remove()
        logger.add(
            sys.stderr,
            colorize=True,
            backtrace=debug,
            diagnose=debug,
            level='DEBUG' if debug else 'INFO',
            format=(
                '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | '
                '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
            ),
        )

        # Route stdlib logging to Loguru
        logging.basicConfig(handlers=[InterceptHandler()], level=level)
    else:
        # Fallback: stdlib logging only
        logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
