"""
Exception utilities: standard boilerplate to log full traceback and re-raise.
상속/데코레이터 형태로 제공하여 예외 삼킴 없이 일관 처리.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Callable, TypeVar, Any, Generator

F = TypeVar("F", bound=Callable[..., Any])


def rethrow_with_trace(logger: logging.Logger | None = None) -> Callable[[F], F]:
    """
    Decorator factory that logs full traceback and re-raises exceptions.

    Usage:
        @rethrow_with_trace()
        def func(...):
            ...
    """

    def _decorator(func: F) -> F:
        log = logger or logging.getLogger(func.__qualname__)

        def _wrapped(*args: Any, **kwargs: Any):  # type: ignore[misc]
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.exception("Unhandled exception in %s", func.__qualname__)
                raise

        return _wrapped  # type: ignore[return-value]

    return _decorator


@contextmanager
def trace_exceptions(logger: logging.Logger, context: str = "") -> Generator[None, None, None]:
    """
    Context manager to log full traceback and re-raise exceptions.
    """
    try:
        yield
    except Exception:
        if context:
            logger.exception("Unhandled exception: %s", context)
        else:
            logger.exception("Unhandled exception")
        raise


class RaiseWithTraceMixin:
    """
    Mixin providing helpers to log full traceback and re-raise.
    하위 클래스에서 self.logger가 있으면 사용, 없으면 클래스명 기반 로거 사용.
    """

    @property
    def _trace_logger(self) -> logging.Logger:
        return getattr(self, "logger", logging.getLogger(self.__class__.__name__))

    def raise_with_trace(self, e: Exception, message: str | None = None) -> None:
        log = self._trace_logger
        if message:
            log.exception(message)
        else:
            log.exception("Unhandled exception")
        raise e

