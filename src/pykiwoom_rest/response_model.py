"""
API Response Model
표준화된 API 응답 모델 클래스
작성일: 2025-01-27
"""

import uuid
from datetime import datetime
from typing import Any, Dict, ItemsView, Iterator, KeysView, Optional, Union, ValuesView


class APIResponse:
    """
    표준화된 API 응답 클래스
    모든 API 응답을 일관된 형태로 제공하며 dict 인터페이스 호환성 유지
    """

    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
        tr_code: Optional[str] = None,
        endpoint: Optional[str] = None,
        processing_time: Optional[float] = None,
    ):
        """
        APIResponse 초기화

        Args:
            success: 요청 성공 여부
            data: 성공시 응답 데이터
            error: 실패시 에러 정보
            tr_code: 키움 TR 코드
            endpoint: API 엔드포인트
            processing_time: 처리 시간 (초)
        """
        self._response_data = {
            "success": success,
            "data": data or {},
            "error": error,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "request_id": str(uuid.uuid4())[:8],
                "tr_code": tr_code,
                "endpoint": endpoint,
                "processing_time": processing_time,
            },
        }

    @classmethod
    def create_success(
        cls,
        data: Dict[str, Any],
        tr_code: Optional[str] = None,
        endpoint: Optional[str] = None,
        processing_time: Optional[float] = None,
    ) -> "APIResponse":
        """
        성공 응답 생성

        Args:
            data: 응답 데이터
            tr_code: 키움 TR 코드
            endpoint: API 엔드포인트
            processing_time: 처리 시간

        Returns:
            성공 APIResponse 인스턴스
        """
        return cls(
            success=True,
            data=data,
            tr_code=tr_code,
            endpoint=endpoint,
            processing_time=processing_time,
        )

    @classmethod
    def create_error(
        cls,
        error_message: str,
        error_code: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
        tr_code: Optional[str] = None,
        endpoint: Optional[str] = None,
        processing_time: Optional[float] = None,
    ) -> "APIResponse":
        """
        에러 응답 생성

        Args:
            error_message: 에러 메시지
            error_code: 에러 코드
            error_details: 추가 에러 정보
            tr_code: 키움 TR 코드
            endpoint: API 엔드포인트
            processing_time: 처리 시간

        Returns:
            에러 APIResponse 인스턴스
        """
        error_info = {
            "message": error_message,
            "code": error_code,
            "details": error_details or {},
        }

        return cls(
            success=False,
            error=error_info,
            tr_code=tr_code,
            endpoint=endpoint,
            processing_time=processing_time,
        )

    @property
    def success(self) -> bool:
        """성공 여부"""
        return self._response_data["success"]

    @property
    def data(self) -> Dict[str, Any]:
        """응답 데이터 (하위 호환성을 위해 data 키의 내용 직접 반환)"""
        return self._response_data["data"]

    @property
    def error(self) -> Optional[Dict[str, Any]]:
        """에러 정보"""
        return self._response_data["error"]

    @property
    def metadata(self) -> Dict[str, Any]:
        """메타데이터 정보"""
        return self._response_data["metadata"]

    @property
    def raw_response(self) -> Dict[str, Any]:
        """전체 응답 구조"""
        return self._response_data.copy()

    # ========== Dict 인터페이스 호환성 ==========

    def __getitem__(self, key: str) -> Any:
        """Dict처럼 키로 접근 (하위 호환성)"""
        # 최상위 키들 먼저 확인
        if key in self._response_data:
            return self._response_data[key]

        # 기존 코드 호환성을 위해 data 내부도 확인
        if key in self._response_data["data"]:
            return self._response_data["data"][key]

        raise KeyError(f"Key '{key}' not found in response")

    def __setitem__(self, key: str, value: Any) -> None:
        """Dict처럼 값 설정 (레거시 호환성)"""
        if key in ["success", "error", "metadata"]:
            self._response_data[key] = value
        else:
            self._response_data["data"][key] = value

    def __contains__(self, key: str) -> bool:
        """'in' 연산자 지원"""
        return key in self._response_data or key in self._response_data["data"]

    def __iter__(self) -> Iterator[str]:
        """반복자 지원 (data 키들 반환)"""
        return iter(self._response_data["data"])

    def __len__(self) -> int:
        """길이 반환 (data 키 개수)"""
        return len(self._response_data["data"])

    def keys(self) -> KeysView[str]:
        """Dict keys() 호환 (data 내용)"""
        return self._response_data["data"].keys()

    def values(self) -> ValuesView[Any]:
        """Dict values() 호환 (data 내용)"""
        return self._response_data["data"].values()

    def items(self) -> ItemsView[str, Any]:
        """Dict items() 호환 (data 내용)"""
        return self._response_data["data"].items()

    def get(self, key: str, default: Any = None) -> Any:
        """Dict get() 호환"""
        try:
            return self[key]
        except KeyError:
            return default

    def update(self, other: Dict[str, Any]) -> None:
        """Dict update() 호환"""
        self._response_data["data"].update(other)

    # ========== 키움 API 특화 메서드 ==========

    def is_kiwoom_success(self) -> bool:
        """키움 API 성공 여부 확인 (rt_cd == '0')"""
        return self.get("rt_cd") == "0"

    def get_kiwoom_message(self) -> Optional[str]:
        """키움 API 메시지 반환"""
        return self.get("msg1")

    def has_output_data(self, output_key: str = "output") -> bool:
        """출력 데이터 존재 여부"""
        return output_key in self._response_data["data"]

    def get_output_data(self, output_key: str = "output") -> Optional[Any]:
        """출력 데이터 반환"""
        return self._response_data["data"].get(output_key)

    # ========== 유틸리티 메서드 ==========

    def to_dict(self) -> Dict[str, Any]:
        """순수 딕셔너리로 변환"""
        return self._response_data.copy()

    def to_legacy_dict(self) -> Dict[str, Any]:
        """기존 형태의 딕셔너리로 변환 (하위 호환성)"""
        return self._response_data["data"].copy()

    def __repr__(self) -> str:
        """객체 표현"""
        status = "SUCCESS" if self.success else "ERROR"
        request_id = self.metadata["request_id"]
        tr_code = self.metadata.get("tr_code", "N/A")
        return f"APIResponse(status={status}, tr_code={tr_code}, id={request_id})"

    def __str__(self) -> str:
        """문자열 표현"""
        return repr(self)

    def __bool__(self) -> bool:
        """Boolean 평가 (성공 여부)"""
        return self.success


# ========== 타입 별칭 ==========

APIResponseType = Union[APIResponse, Dict[str, Any]]
