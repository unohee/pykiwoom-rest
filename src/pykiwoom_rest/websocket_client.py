# Task: TM-20251029-001 | 생성: 2025-10-29 | PRD: FR-001, FR-008
# 목적: WebSocket 연결 관리 및 실시간 데이터 수신 | 의존성: websockets, asyncio
# CI상태: [pending]

"""
WebSocket 클라이언트 모듈

Kiwoom증권 REST API의 실시간 시세 WebSocket 연결을 관리합니다.
"""

import asyncio
import contextlib
import inspect
import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Set

try:
    import websockets
except ImportError:
    raise ImportError("websockets 라이브러리가 필요합니다. 설치하려면: pip install websockets")


logger = logging.getLogger(__name__)


class WebSocketClient:
    """
    Kiwoom 실시간 시세 WebSocket 클라이언트

    Features:
        - 자동 연결/재연결
        - 다중 종목 구독 관리
        - 이벤트 기반 콜백
        - 하트비트 및 타임아웃 처리
    """

    def __init__(
        self,
        base_url: str,
        access_token: str,
        appkey: str,
        appsecret: str,
        api_id: str = "0B",
        auto_reconnect: bool = True,
        reconnect_interval: int = 5,
        max_reconnect_attempts: int = 10,
        ping_interval: int = 30,
        ping_timeout: int = 10,
    ):
        """
        WebSocket 클라이언트 초기화

        Args:
            base_url: WebSocket 베이스 URL (예: wss://api.kiwoom.com:10000)
            access_token: OAuth2 액세스 토큰
            appkey: 앱키 (호환성용, Kiwoom WebSocket 헤더에는 사용하지 않음)
            appsecret: 앱시크릿 (호환성용, Kiwoom WebSocket 헤더에는 사용하지 않음)
            api_id: 연결 요청 Header api-id 기본값
            auto_reconnect: 자동 재연결 활성화
            reconnect_interval: 재연결 간격 (초)
            max_reconnect_attempts: 최대 재연결 시도 횟수
            ping_interval: 하트비트 간격 (초)
            ping_timeout: 하트비트 타임아웃 (초)
        """
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.appkey = appkey
        self.appsecret = appsecret
        self.api_id = api_id

        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout

        self._ws: Optional[Any] = None
        self._connected = False
        self._subscriptions: Set[str] = set()  # {tr_id}:{tr_key} 형식
        self._callbacks: Dict[str, Callable] = {}  # subscription_key 또는 tr_id -> callback
        self._reconnect_count = 0
        self._last_message_time = datetime.now()
        self._receive_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
        self._group_no = "1"

    @property
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        if not self._connected or self._ws is None:
            return False
        closed = getattr(self._ws, "closed", None)
        if closed is not None:
            return not closed
        close_code = getattr(self._ws, "close_code", None)
        return close_code is None

    def _connect_header_kwargs(self, headers: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """websockets 버전에 맞는 header 인자명 반환."""
        try:
            parameters = inspect.signature(websockets.connect).parameters
        except (TypeError, ValueError):
            parameters = {}
        if "additional_headers" in parameters:
            return {"additional_headers": headers}
        return {"extra_headers": headers}

    def _connect_headers(self, api_id: Optional[str] = None) -> Dict[str, str]:
        return {
            "authorization": f"Bearer {self.access_token}",
            "api-id": api_id or self.api_id,
        }

    @staticmethod
    def _subscription_key(tr_id: str, tr_key: str) -> str:
        return f"{tr_id}:{tr_key}"

    def _build_subscription_message(self, tr_id: str, tr_key: str, trnm: str) -> Dict[str, Any]:
        message = {
            "trnm": trnm,
            "grp_no": self._group_no,
            "data": [{"item": [tr_key], "type": [tr_id]}],
        }
        if trnm == "REG":
            message["refresh"] = "1"
        return message

    async def _close_connection(self, clear_subscriptions: bool = False):
        """현재 socket/task를 정리한다. 재연결 시 구독 목록은 보존한다."""
        self._connected = False
        current_task = asyncio.current_task()

        for attr in ("_receive_task", "_ping_task"):
            task = getattr(self, attr)
            if task and task is not current_task and not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task
            if task is not current_task:
                setattr(self, attr, None)

        if self._ws:
            with contextlib.suppress(Exception):
                await self._ws.close()
            self._ws = None

        if clear_subscriptions:
            self._subscriptions.clear()

    async def connect(self, api_id: Optional[str] = None) -> bool:
        """
        WebSocket 서버에 연결

        Returns:
            연결 성공 여부
        """
        if self.is_connected:
            logger.info("이미 WebSocket에 연결되어 있습니다.")
            return True

        try:
            ws_url = f"{self.base_url}/api/dostk/websocket"
            headers = self._connect_headers(api_id)

            logger.info(f"WebSocket 연결 시도: {ws_url}")
            self._ws = await websockets.connect(
                ws_url,
                **self._connect_header_kwargs(headers),
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
            )

            self._connected = True
            self._reconnect_count = 0
            self._last_message_time = datetime.now()
            logger.info("WebSocket 연결 성공")

            # 메시지 수신 태스크 시작
            self._receive_task = asyncio.create_task(self._receive_loop())
            self._ping_task = asyncio.create_task(self._ping_loop())

            # 기존 구독 복원
            await self._restore_subscriptions()

            return True

        except Exception as e:
            logger.error(f"WebSocket 연결 실패: {e}")
            self._connected = False
            if self.auto_reconnect:
                await self._attempt_reconnect()
            return False

    async def disconnect(self):
        """WebSocket 연결 종료"""
        await self._close_connection(clear_subscriptions=True)
        logger.info("WebSocket 연결 종료")

    async def subscribe(self, tr_id: str, tr_key: str, callback: Optional[Callable] = None) -> bool:
        """
        실시간 데이터 구독

        Args:
            tr_id: TR 코드 (예: "0B" - 주식체결, "0D" - 주식호가잔량)
            tr_key: 종목코드 또는 계좌번호
            callback: 데이터 수신 시 호출될 콜백 함수 (선택)

        Returns:
            구독 성공 여부
        """
        if not self.is_connected:
            logger.error("WebSocket이 연결되지 않았습니다.")
            return False

        subscription_key = self._subscription_key(tr_id, tr_key)
        if subscription_key in self._subscriptions:
            logger.info(f"이미 구독 중: {subscription_key}")
            return True

        try:
            subscribe_msg = self._build_subscription_message(tr_id, tr_key, "REG")

            await self._ws.send(json.dumps(subscribe_msg))
            self._subscriptions.add(subscription_key)

            if callback:
                self._callbacks[subscription_key] = callback
            elif tr_id in self._callbacks:
                self._callbacks[subscription_key] = self._callbacks[tr_id]

            logger.info(f"구독 성공: {subscription_key}")
            return True

        except Exception as e:
            logger.error(f"구독 실패: {e}")
            return False

    async def unsubscribe(self, tr_id: str, tr_key: str) -> bool:
        """
        실시간 데이터 구독 해제

        Args:
            tr_id: TR 코드
            tr_key: 종목코드 또는 계좌번호

        Returns:
            구독 해제 성공 여부
        """
        subscription_key = self._subscription_key(tr_id, tr_key)
        if subscription_key not in self._subscriptions:
            logger.warning(f"구독하지 않은 항목: {subscription_key}")
            return False

        try:
            unsubscribe_msg = self._build_subscription_message(tr_id, tr_key, "REMOVE")

            await self._ws.send(json.dumps(unsubscribe_msg))
            self._subscriptions.discard(subscription_key)
            self._callbacks.pop(subscription_key, None)

            logger.info(f"구독 해제 성공: {subscription_key}")
            return True

        except Exception as e:
            logger.error(f"구독 해제 실패: {e}")
            return False

    async def _receive_loop(self):
        """메시지 수신 루프"""
        try:
            async for message in self._ws:
                self._last_message_time = datetime.now()
                await self._handle_message(message)
        except asyncio.CancelledError:
            logger.info("메시지 수신 루프 종료")
        except Exception as e:
            logger.error(f"메시지 수신 오류: {e}")
            if self.auto_reconnect:
                await self._attempt_reconnect()

    async def _ping_loop(self):
        """하트비트 및 타임아웃 감지 루프"""
        while self.is_connected:
            await asyncio.sleep(self.ping_interval)

            # 마지막 메시지 수신 시간 확인
            elapsed = (datetime.now() - self._last_message_time).total_seconds()
            if elapsed > self.ping_timeout + self.ping_interval:
                logger.warning(f"서버 응답 없음 ({elapsed:.1f}초), 재연결 시도")
                if self.auto_reconnect:
                    await self._attempt_reconnect()
                break

    async def _handle_message(self, message: str):
        """수신한 메시지 처리"""
        try:
            data = json.loads(message)
            if data.get("trnm") == "REAL" and isinstance(data.get("data"), list):
                for realtime_data in data["data"]:
                    await self._dispatch_realtime_data(realtime_data, data)
                return

            tr_id = data.get("header", {}).get("tr_id") or data.get("type")
            tr_key = data.get("header", {}).get("tr_key") or data.get("item")
            await self._dispatch_callback(tr_id, tr_key, data)

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}, 메시지: {message}")
        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")

    async def _dispatch_realtime_data(self, realtime_data: Dict[str, Any], raw_message: Dict[str, Any]):
        tr_id = realtime_data.get("type")
        tr_key = realtime_data.get("item")
        event = dict(realtime_data)
        event["_raw"] = raw_message
        await self._dispatch_callback(tr_id, tr_key, event)

    async def _dispatch_callback(self, tr_id: Optional[str], tr_key: Optional[str], data: Dict[str, Any]):
        if not tr_id:
            logger.debug("TR 코드 없는 메시지")
            return

        callback = None
        if tr_key:
            callback = self._callbacks.get(self._subscription_key(tr_id, tr_key))
        if callback is None:
            callback = self._callbacks.get(tr_id)

        if callback is None:
            logger.debug(f"콜백 없는 메시지: {tr_id}:{tr_key}")
            return

        if asyncio.iscoroutinefunction(callback):
            await callback(data)
        else:
            callback(data)

    async def _restore_subscriptions(self):
        """연결 복구 후 기존 구독 복원"""
        if not self._subscriptions:
            return

        logger.info(f"기존 구독 복원 중: {len(self._subscriptions)}개")
        for subscription_key in list(self._subscriptions):
            tr_id, tr_key = subscription_key.split(":", 1)
            callback = self._callbacks.get(subscription_key) or self._callbacks.get(tr_id)
            # 구독 목록에서 제거 후 다시 구독 (중복 방지)
            self._subscriptions.discard(subscription_key)
            await self.subscribe(tr_id, tr_key, callback)

    async def _attempt_reconnect(self):
        """재연결 시도"""
        if not self.auto_reconnect:
            return

        self._reconnect_count += 1
        if self._reconnect_count > self.max_reconnect_attempts:
            logger.error("최대 재연결 시도 횟수 초과")
            return

        logger.info(
            f"재연결 시도 {self._reconnect_count}/{self.max_reconnect_attempts} "
            f"({self.reconnect_interval}초 후)"
        )
        await self._close_connection(clear_subscriptions=False)
        await asyncio.sleep(self.reconnect_interval)
        await self.connect()

    def register_callback(self, tr_id: str, callback: Callable):
        """
        TR 코드별 콜백 등록

        Args:
            tr_id: TR 코드
            callback: 콜백 함수 (동기/비동기 모두 지원)
        """
        self._callbacks[tr_id] = callback
        logger.info(f"콜백 등록: {tr_id}")

    def unregister_callback(self, tr_id: str):
        """
        TR 코드별 콜백 제거

        Args:
            tr_id: TR 코드
        """
        removed = False
        for key in list(self._callbacks):
            if key == tr_id or key.startswith(f"{tr_id}:"):
                del self._callbacks[key]
                removed = True
        if removed:
            logger.info(f"콜백 제거: {tr_id}")
