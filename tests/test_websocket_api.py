# Task: TM-20251029-001 | 생성: 2025-10-29 | PRD: NFR-006
# 목적: WebSocket API 테스트 | 의존성: pytest, pytest-asyncio
# CI상태: [pending]

"""
WebSocket API 테스트

실시간 시세 WebSocket API 기능을 검증합니다.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from pykiwoom_rest.websocket_api import (
    WebSocketAPI,
    RealtimeQuote,
    RealtimeOrderbook,
    RealtimeTrade,
)
from pykiwoom_rest.websocket_client import WebSocketClient


class TestWebSocketClient:
    """WebSocketClient 테스트"""

    @pytest.fixture
    def ws_client(self):
        """WebSocketClient 인스턴스 생성"""
        return WebSocketClient(
            base_url="wss://test.example.com",
            access_token="test_token",
            appkey="test_appkey",
            appsecret="test_appsecret",
            auto_reconnect=False,  # 테스트 중 자동 재연결 비활성화
        )

    def test_init(self, ws_client):
        """초기화 테스트"""
        assert ws_client.base_url == "wss://test.example.com"
        assert ws_client.access_token == "test_token"
        assert ws_client.appkey == "test_appkey"
        assert ws_client.appsecret == "test_appsecret"
        assert not ws_client.is_connected

    @pytest.mark.asyncio
    async def test_connect_success(self, ws_client):
        """연결 성공 테스트"""
        with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.closed = False
            mock_connect.return_value = mock_ws

            # 메시지 수신 루프 모의
            async def mock_iter():
                await asyncio.sleep(0.1)  # 짧은 대기
                return
                yield  # pragma: no cover

            mock_ws.__aiter__.return_value = mock_iter()

            result = await ws_client.connect()

            assert result is True
            assert ws_client.is_connected
            mock_connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect(self, ws_client):
        """연결 종료 테스트"""
        # 연결 모의
        mock_ws = AsyncMock()
        ws_client._ws = mock_ws
        ws_client._connected = True

        await ws_client.disconnect()

        assert not ws_client.is_connected
        mock_ws.close.assert_called_once()


class TestWebSocketAPI:
    """WebSocketAPI 테스트"""

    @pytest.fixture
    def ws_api(self):
        """WebSocketAPI 인스턴스 생성"""
        return WebSocketAPI(
            access_token="test_token",
            appkey="test_appkey",
            appsecret="test_appsecret",
            base_url="wss://test.example.com",
            auto_reconnect=False,
        )

    def test_init(self, ws_api):
        """초기화 테스트"""
        assert ws_api._client is not None
        assert not ws_api.is_connected

    @pytest.mark.asyncio
    async def test_connect(self, ws_api):
        """연결 테스트"""
        with patch.object(ws_api._client, "connect", return_value=True):
            result = await ws_api.connect()
            assert result is True

    @pytest.mark.asyncio
    async def test_disconnect(self, ws_api):
        """연결 종료 테스트"""
        with patch.object(ws_api._client, "disconnect"):
            await ws_api.disconnect()
            ws_api._client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe_quote(self, ws_api):
        """실시간 시세 구독 테스트"""
        callback_called = False

        def callback(quote: RealtimeQuote):
            nonlocal callback_called
            callback_called = True
            assert quote.stock_code == "005930"

        with patch.object(ws_api._client, "subscribe", return_value=True) as mock_sub:
            with patch.object(ws_api._client, "register_callback"):
                result = await ws_api.subscribe_quote("005930", callback)
                assert result is True
                mock_sub.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe_orderbook(self, ws_api):
        """실시간 호가 구독 테스트"""
        with patch.object(ws_api._client, "subscribe", return_value=True) as mock_sub:
            with patch.object(ws_api._client, "register_callback"):
                result = await ws_api.subscribe_orderbook("005930")
                assert result is True
                mock_sub.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe_trade(self, ws_api):
        """실시간 체결 구독 테스트"""
        with patch.object(ws_api._client, "subscribe", return_value=True) as mock_sub:
            with patch.object(ws_api._client, "register_callback"):
                result = await ws_api.subscribe_trade("005930")
                assert result is True
                mock_sub.assert_called_once()

    @pytest.mark.asyncio
    async def test_unsubscribe_quote(self, ws_api):
        """실시간 시세 구독 해제 테스트"""
        with patch.object(
            ws_api._client, "unsubscribe", return_value=True
        ) as mock_unsub:
            result = await ws_api.unsubscribe_quote("005930")
            assert result is True
            mock_unsub.assert_called_once()

    def test_parse_quote(self, ws_api):
        """실시간 시세 데이터 파싱 테스트"""
        data = {
            "body": {
                "output": {
                    "stck_prpr": "70000",
                    "prdy_vrss": "1000",
                    "prdy_ctrt": "1.45",
                    "acml_vol": "1000000",
                    "stck_oprc": "69000",
                    "stck_hgpr": "71000",
                    "stck_lwpr": "68000",
                }
            }
        }

        quote = ws_api._parse_quote("005930", data)

        assert quote.stock_code == "005930"
        assert quote.current_price == 70000
        assert quote.change_price == 1000
        assert quote.change_rate == 1.45
        assert quote.volume == 1000000
        assert quote.open_price == 69000
        assert quote.high_price == 71000
        assert quote.low_price == 68000

    def test_parse_orderbook(self, ws_api):
        """실시간 호가 데이터 파싱 테스트"""
        data = {
            "body": {
                "output": {
                    "askp1": "70100",
                    "askp2": "70200",
                    "askp_rsqn1": "100",
                    "askp_rsqn2": "200",
                    "bidp1": "69900",
                    "bidp2": "69800",
                    "bidp_rsqn1": "150",
                    "bidp_rsqn2": "250",
                }
            }
        }

        orderbook = ws_api._parse_orderbook("005930", data)

        assert orderbook.stock_code == "005930"
        assert len(orderbook.ask_prices) == 10
        assert orderbook.ask_prices[0] == 70100
        assert orderbook.bid_prices[0] == 69900

    def test_parse_trade(self, ws_api):
        """실시간 체결 데이터 파싱 테스트"""
        data = {
            "body": {
                "output": {
                    "stck_cntg_hour": "70000",
                    "cntg_vol": "100",
                    "prdy_vrss": "500",
                    "prdy_ctrt": "0.72",
                    "acml_vol": "1500000",
                }
            }
        }

        trade = ws_api._parse_trade("005930", data)

        assert trade.stock_code == "005930"
        assert trade.trade_price == 70000
        assert trade.trade_volume == 100
        assert trade.change_price == 500


class TestDataClasses:
    """데이터 클래스 테스트"""

    def test_realtime_quote(self):
        """RealtimeQuote 데이터 클래스 테스트"""
        quote = RealtimeQuote(
            stock_code="005930",
            current_price=70000,
            change_price=1000,
            change_rate=1.45,
            volume=1000000,
            timestamp=datetime.now(),
        )

        assert quote.stock_code == "005930"
        assert quote.current_price == 70000
        assert quote.volume == 1000000

    def test_realtime_orderbook(self):
        """RealtimeOrderbook 데이터 클래스 테스트"""
        orderbook = RealtimeOrderbook(
            stock_code="005930",
            timestamp=datetime.now(),
            ask_prices=[70100, 70200],
            bid_prices=[69900, 69800],
        )

        assert orderbook.stock_code == "005930"
        assert len(orderbook.ask_prices) == 2
        assert len(orderbook.bid_prices) == 2

    def test_realtime_trade(self):
        """RealtimeTrade 데이터 클래스 테스트"""
        trade = RealtimeTrade(
            stock_code="005930",
            trade_price=70000,
            trade_volume=100,
            trade_time="153000",
            timestamp=datetime.now(),
        )

        assert trade.stock_code == "005930"
        assert trade.trade_price == 70000
        assert trade.trade_volume == 100


class TestKiwoomRestIntegration:
    """KiwoomRest Facade 통합 테스트"""

    @pytest.fixture
    def kiwoom(self):
        """KiwoomRest 인스턴스 생성 (모의)"""
        from pykiwoom_rest import KiwoomRest

        with patch("pykiwoom_rest.kiwoom_base.KiwoomAPIBase._setup_credentials"):
            kiwoom = KiwoomRest(
                account_no="test",
                appkey="test_appkey",
                appsecret="test_appsecret",
            )
            # 토큰 및 인증 정보 모의 설정
            kiwoom.auth_api.access_token = "test_token"
            kiwoom.stock_api.api_base.appkey = "test_appkey"
            kiwoom.stock_api.api_base.appsecret = "test_appsecret"
            return kiwoom

    def test_websocket_property(self, kiwoom):
        """websocket 프로퍼티 테스트"""
        # websocket 속성 접근 (lazy initialization)
        ws = kiwoom.websocket
        assert ws is not None
        assert isinstance(ws, WebSocketAPI)

    def test_enable_websocket(self, kiwoom):
        """WebSocket 활성화 테스트"""
        with patch("asyncio.get_event_loop") as mock_loop:
            with patch.object(
                kiwoom._websocket_api or kiwoom.websocket,
                "connect",
                new_callable=AsyncMock,
            ) as mock_connect:
                mock_connect.return_value = True
                mock_loop.return_value.run_until_complete.return_value = True
                result = kiwoom.enable_websocket()
                assert result is True

    def test_subscribe_realtime_quote_without_enable(self, kiwoom):
        """WebSocket 미활성화 상태에서 구독 시도 테스트"""
        with pytest.raises(RuntimeError, match="WebSocket이 활성화되지 않았습니다"):
            kiwoom.subscribe_realtime_quote("005930")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
