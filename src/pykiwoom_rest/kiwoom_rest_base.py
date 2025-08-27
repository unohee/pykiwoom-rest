"""
Legacy KiwoomRestBase for backward compatibility
하위 호환성을 위한 레거시 베이스 클래스
"""

from .kiwoom_base import KiwoomAPIBase


class KiwoomRestBase(KiwoomAPIBase):
    """
    하위 호환성을 위한 KiwoomRestBase
    기존 코드와의 호환성 유지를 위해 제공
    """
    pass