"""Kiwoom CLI — LLM 친화형 키움증권 REST API CLI."""


def main():
    """CLI 진입점을 지연 로드한다."""
    from .main import main as run

    return run()


__all__ = ["main"]
