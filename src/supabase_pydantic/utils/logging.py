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


# helpers


def _coerce_level(level: int | str | None) -> int:
    """Accept int (10/20/30/40), or str ('DEBUG'/'INFO'/...), default INFO."""
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        return logging._nameToLevel.get(level.upper(), logging.INFO)
    return logging.INFO


def _want_caller_details(effective_level: int) -> bool:
    """Show file:line and function when at DEBUG or lower (i.e., more verbose)."""
    return effective_level <= logging.DEBUG


# stdlib → loguru bridge


class InterceptHandler(logging.Handler):
    """Redirect standard logging records to Loguru if available."""

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - trivial  # noqa: D102
        if not _HAS_LOGURU or logger is None:
            return

        try:
            lvl = logger.level(record.levelname).name
        except Exception:
            lvl = record.levelno  # type: ignore

        # Compute correct depth by skipping frames from stdlib logging module
        frame: FrameType | None = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == getattr(logging, '__file__', None):
            frame = frame.f_back
            depth += 1

        logger.bind(logger_name=record.name).opt(depth=depth, exception=record.exc_info).log(lvl, record.getMessage())


# main setup


def setup_logging(
    level: int | str = 'INFO',
    *,
    # Full timestamp with date and time
    loguru_timefmt: str = 'YYYY-MM-DD HH:mm:ss',
    stdlib_datefmt: str = '%Y-%m-%d %H:%M:%S',
    include_ms: bool = False,
    force: bool = False,  # Python 3.8+: override pre-existing handlers
) -> None:
    """Configure Loguru if available; otherwise stdlib logging.

    Args:
        level: Desired log level (e.g., "DEBUG", "INFO", 20, etc.).
        loguru_timefmt: Time format for Loguru (e.g., "YYYY-MM-DD HH:mm:ss").
        stdlib_datefmt: Time format for stdlib (strftime, e.g., "%Y-%m-%d %H:%M:%S").
        include_ms: Append milliseconds in both Loguru and stdlib outputs.
        force: If True and Python>=3.8, force override existing handlers.
    """

    # If TRACE (5) is requested but Loguru isn't available, bump to DEBUG
    effective_level = _coerce_level(level)
    if effective_level == 5 and not (_HAS_LOGURU and logger is not None):
        effective_level = logging.DEBUG

    debug_details = _want_caller_details(effective_level)

    # ----- LOGURU BRANCH -----
    if _HAS_LOGURU and logger is not None:
        # Remove existing handlers configured by other libs
        logging.root.handlers = []
        logging.root.setLevel(effective_level)

        # Build Loguru format with dashes between components
        # Example:
        #  2023-09-12 14:30:15 - INFO - message
        parts = [
            f'<green>{{time:{loguru_timefmt + (".SSS" if include_ms and ".SSS" not in loguru_timefmt else "")}}}</green>',  # noqa: E501
            '<level>{level}</level>',
        ]
        if debug_details:
            parts.append('<cyan>{file.name}:{line}</cyan> {function}()')
        parts.append('{message}')
        loguru_fmt = ' - '.join(parts)

        logger.remove()
        logger.add(
            sys.stderr,
            colorize=True,
            backtrace=(effective_level <= logging.DEBUG),
            diagnose=(effective_level <= logging.DEBUG),
            level=effective_level,
            format=loguru_fmt,
        )

        # Route stdlib logging to Loguru
        kwargs = {'handlers': [InterceptHandler()], 'level': effective_level}
        if force and hasattr(logging, 'basicConfig'):
            kwargs['force'] = True  # type: ignore[arg-type]
        logging.basicConfig(**kwargs)  # type: ignore
        return

    # ----- STDLIB FALLBACK -----
    # Build stdlib format with dashes between components
    # 2023-09-12 14:30:15 - INFO - message
    asctime = '%(asctime)s' + ('.%(msecs)03d' if include_ms else '')
    parts = [asctime, '%(levelname)s']
    if debug_details:
        parts.append('%(filename)s:%(lineno)d %(funcName)s()')
    parts.append('%(message)s')
    stdlib_fmt = ' - '.join(parts)

    kwargs = dict(
        level=effective_level,
        format=stdlib_fmt,
        datefmt=stdlib_datefmt,
    )
    if force and hasattr(logging, 'basicConfig'):
        kwargs['force'] = True  # type: ignore[assignment]
    logging.basicConfig(**kwargs)  # type: ignore
