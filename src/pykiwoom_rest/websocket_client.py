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
from urllib.parse import urlparse

try:  # pragma: no cover - imported during pytest collection before coverage starts
    import websockets
except ImportError as exc:  # pragma: no cover - verified in isolated import test
    raise ImportError("websockets 라이브러리가 필요합니다. 설치하려면: pip install websockets") from exc


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
        if urlparse(self.base_url).scheme != "wss":
            raise ValueError("WebSocket base_url must use wss://")
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
        self._subscription_lock = asyncio.Lock()
        self._reconnect_count = 0
        self._reconnect_attempts_exhausted = False
        self._last_message_time = datetime.now()
        self._receive_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
        self._reconnect_lock = asyncio.Lock()
        self._group_no = "1"
        self._pending_acks: Dict[str, asyncio.Future] = {}
        self._ack_lock = asyncio.Lock()
        self._ack_timeout = 5

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

    def _ack_key(self, trnm: str, tr_id: str, tr_key: str) -> str:
        return f"{trnm}:{self._subscription_key(tr_id, tr_key)}"

    def _create_ack_future(self, trnm: str, tr_id: str, tr_key: str) -> asyncio.Future:
        future = asyncio.get_running_loop().create_future()
        self._pending_acks[self._ack_key(trnm, tr_id, tr_key)] = future
        return future

    def _clear_ack_future(self, trnm: str, tr_id: str, tr_key: str, future: asyncio.Future):
        ack_key = self._ack_key(trnm, tr_id, tr_key)
        if self._pending_acks.get(ack_key) is future:
            self._pending_acks.pop(ack_key, None)

    async def _send_subscription_message(self, trnm: str, tr_id: str, tr_key: str) -> bool:
        async with self._ack_lock:
            future = self._create_ack_future(trnm, tr_id, tr_key)
            try:
                await self._ws.send(json.dumps(self._build_subscription_message(tr_id, tr_key, trnm)))
                return await self._wait_for_ack(trnm, tr_id, tr_key, future)
            finally:
                self._clear_ack_future(trnm, tr_id, tr_key, future)

    async def _wait_for_ack(self, trnm: str, tr_id: str, tr_key: str, future: asyncio.Future) -> bool:
        try:
            ack = await asyncio.wait_for(future, timeout=self._ack_timeout)
        except asyncio.TimeoutError:
            logger.error(f"WebSocket {trnm} ACK 대기 시간 초과: {tr_id}:{tr_key}")
            return False
        except ConnectionError as e:
            logger.error(f"WebSocket {trnm} ACK 대기 중 연결 종료: {e}")
            return False

        return_code = str(ack.get("return_code", ""))
        if return_code not in {"0", "000000"}:
            logger.error(f"WebSocket {trnm} 실패: {ack.get('return_msg') or return_code}")
            return False
        return True

    def _resolve_ack(self, message: Dict[str, Any]) -> bool:
        trnm = message.get("trnm")
        if trnm not in {"REG", "REMOVE"}:
            return False
        for data in message.get("data") or []:
            for tr_id in data.get("type") or []:
                for tr_key in data.get("item") or []:
                    future = self._pending_acks.pop(self._ack_key(trnm, tr_id, tr_key), None)
                    if future is None:
                        continue
                    if not future.done():
                        future.set_result(message)
                    return True
        return False

    def _fail_pending_acks(self):
        for future in self._pending_acks.values():
            if not future.done():
                future.set_exception(ConnectionError("WebSocket connection closed"))
        self._pending_acks.clear()

    async def _close_connection(self, clear_subscriptions: bool = False):
        """현재 socket/task를 정리한다. 재연결 시 구독 목록은 보존한다."""
        self._connected = False
        self._fail_pending_acks()
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
            for subscription_key in self._subscriptions:
                self._callbacks.pop(subscription_key, None)
            self._subscriptions.clear()

    async def connect(self, api_id: Optional[str] = None) -> bool:
        """
        WebSocket 서버에 연결

        Returns:
            연결 성공 여부
        """
        if self.is_connected:
            logger.warning("이미 WebSocket에 연결되어 있습니다")
            return True

        await self._close_connection(clear_subscriptions=False)

        try:
            api_id = api_id or self.api_id
            ws_url = self.base_url
            headers = self._connect_headers(api_id)

            logger.info(f"WebSocket 연결 시도: {ws_url}")
            self._ws = await websockets.connect(
                ws_url,
                **self._connect_header_kwargs(headers),
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
            )

            self._connected = True
            self._last_message_time = datetime.now()
            logger.info("WebSocket 연결 성공")

            # 메시지 수신 태스크 시작
            self._receive_task = asyncio.create_task(self._receive_loop())

            # 기존 구독 복원
            if not await self._restore_subscriptions():
                await self._close_connection(clear_subscriptions=False)
                return False

            self._reconnect_count = 0
            self._reconnect_attempts_exhausted = False
            return True

        except Exception as e:
            logger.error(f"WebSocket 연결 실패: {e}")
            await self._close_connection(clear_subscriptions=False)
            return False

    async def disconnect(self):
        """WebSocket 연결 종료"""
        await self._close_connection(clear_subscriptions=True)
        logger.info("WebSocket 연결 종료")

    async def subscribe(self, tr_id: str, tr_key: str, callback: Optional[Callable] = None) -> bool:
        """
        실시간 데이터 구독

        Args:
            tr_id: TR 코드 (예: 0B - 주식체결)
            tr_key: 종목코드
            callback: 수신 데이터 콜백 함수

        Returns:
            구독 성공 여부
        """
        if not self.is_connected:
            logger.error("WebSocket이 연결되지 않았습니다")
            return False

        subscription_key = self._subscription_key(tr_id, tr_key)
        async with self._subscription_lock:
            if subscription_key in self._subscriptions:
                logger.info(f"이미 구독 중: {subscription_key}")
                if callback:
                    self._callbacks[subscription_key] = callback
                return True

        try:
            success = await self._send_subscription_message("REG", tr_id, tr_key)
            if success:
                async with self._subscription_lock:
                    self._subscriptions.add(subscription_key)
                    if callback:
                        self._callbacks[subscription_key] = callback
                    elif tr_id in self._callbacks:
                        self._callbacks[subscription_key] = self._callbacks[tr_id]
                logger.info(f"실시간 데이터 구독 성공: {subscription_key}")
                return True
            return False
        except Exception as e:
            logger.error(f"실시간 데이터 구독 실패: {e}")
            return False

    async def unsubscribe(self, tr_id: str, tr_key: str) -> bool:
        """
        실시간 데이터 구독 해제

        Args:
            tr_id: TR 코드
            tr_key: 종목코드

        Returns:
            구독 해제 성공 여부
        """
        if not self.is_connected:
            logger.error("WebSocket이 연결되지 않았습니다")
            return False

        subscription_key = self._subscription_key(tr_id, tr_key)
        async with self._subscription_lock:
            if subscription_key not in self._subscriptions:
                logger.warning(f"구독 중이 아님: {subscription_key}")
                return True

        try:
            success = await self._send_subscription_message("REMOVE", tr_id, tr_key)
            if success:
                async with self._subscription_lock:
                    self._subscriptions.discard(subscription_key)
                    self._callbacks.pop(subscription_key, None)
                logger.info(f"실시간 데이터 구독 해제 성공: {subscription_key}")
                return True
            return False
        except Exception as e:
            logger.error(f"실시간 데이터 구독 해제 실패: {e}")
            return False

    async def _receive_loop(self):
        """수신 메시지를 처리하고 연결 오류 시 재연결한다."""
        try:
            async for message in self._ws:
                self._last_message_time = datetime.now()
                await self._handle_message(message)
        except asyncio.CancelledError:
            logger.info("메시지 수신 루프 종료")
            raise
        except Exception as exc:
            logger.error(f"메시지 수신 오류: {exc}")
            if self.auto_reconnect:
                await self._attempt_reconnect()

    async def _ping_loop(self):
        """서버 응답이 장시간 없을 때 재연결한다."""
        while self.is_connected:
            await asyncio.sleep(self.ping_interval)
            elapsed = (datetime.now() - self._last_message_time).total_seconds()
            if elapsed > self.ping_timeout + self.ping_interval:
                logger.warning(f"서버 응답 없음 ({elapsed:.1f}초), 재연결 시도")
                if self.auto_reconnect:
                    await self._attempt_reconnect()
                return

    async def _handle_message(self, message: str):
        """Kiwoom ACK 또는 실시간 데이터 메시지를 처리한다."""
        try:
            data = json.loads(message)
        except json.JSONDecodeError as exc:
            logger.error(f"JSON 파싱 오류: {exc}, 메시지: {message}")
            return

        try:
            if self._resolve_ack(data):
                return
            if data.get("trnm") == "REAL" and isinstance(data.get("data"), list):
                for realtime_data in data["data"]:
                    await self._dispatch_realtime_data(realtime_data, data)
                return

            tr_id = data.get("header", {}).get("tr_id") or data.get("type")
            tr_key = data.get("header", {}).get("tr_key") or data.get("item")
            await self._dispatch_callback(tr_id, tr_key, data)
        except Exception as exc:
            logger.error(f"메시지 처리 오류: {exc}")

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

        callback = self._callbacks.get(self._subscription_key(tr_id, tr_key)) if tr_key else None
        callback = callback or self._callbacks.get(tr_id)
        if callback is None:
            logger.debug(f"콜백 없는 메시지: {tr_id}:{tr_key}")
            return
        result = callback(data)
        if inspect.isawaitable(result):
            await result

    async def _restore_subscriptions(self) -> bool:
        """재연결 후 구독 복원"""
        async with self._subscription_lock:
            subscriptions = list(self._subscriptions)
            callbacks = {key: self._callbacks.get(key) for key in subscriptions}

        if not subscriptions:
            return True

        logger.info(f"구독 복원 시작: {len(subscriptions)}개")
        restored = True

        for subscription_key in subscriptions:
            try:
                tr_id, tr_key = subscription_key.split(":", 1)
                success = await self._send_subscription_message("REG", tr_id, tr_key)
                if success:
                    async with self._subscription_lock:
                        self._subscriptions.add(subscription_key)
                        callback = callbacks.get(subscription_key)
                        if callback:
                            self._callbacks[subscription_key] = callback
                    logger.info(f"구독 복원 성공: {subscription_key}")
                else:
                    logger.error(f"구독 복원 실패: {subscription_key}")
                    restored = False
            except Exception as e:
                logger.error(f"구독 복원 실패 {subscription_key}: {e}")
                restored = False

        return restored

    async def _attempt_reconnect(self):
        """WebSocket 재연결 시도"""
        async with self._reconnect_lock:
            if self._reconnect_attempts_exhausted:
                logger.error("최대 재연결 시도 횟수가 이미 초과되었습니다")
                return False

            while self._reconnect_count < self.max_reconnect_attempts:
                self._reconnect_count += 1
                logger.info(
                    f"재연결 시도 {self._reconnect_count}/{self.max_reconnect_attempts} "
                    f"({self.reconnect_interval}초 후)"
                )

                await self._close_connection(clear_subscriptions=False)
                await asyncio.sleep(self.reconnect_interval)

                try:
                    headers = self._connect_headers()
                    self._ws = await websockets.connect(
                        self.base_url,
                        **self._connect_header_kwargs(headers),
                        ping_interval=self.ping_interval,
                        ping_timeout=self.ping_timeout,
                    )
                    self._connected = True
                    self._last_message_time = datetime.now()

                    logger.info("WebSocket 재연결 성공")
                    self._receive_task = asyncio.create_task(self._receive_loop())
                    if not await self._restore_subscriptions():
                        raise RuntimeError("failed to restore subscriptions")
                    self._reconnect_count = 0
                    self._reconnect_attempts_exhausted = False
                    return True
                except Exception as e:
                    logger.error(f"WebSocket 재연결 실패: {e}")
                    await self._close_connection(clear_subscriptions=False)

            logger.error("최대 재연결 시도 횟수 초과")
            self._reconnect_attempts_exhausted = True
            return False

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
