"""
Chart Data API
차트 데이터 관련 API 클래스
작성일: 2025-01-27
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .kiwoom_base import KiwoomAPIBase


class ChartAPI(KiwoomAPIBase):
    """차트 데이터 관련 API"""
    
    # TR 코드 매핑
    TR_CODES = {
        'tick_chart': 'ka10079',
        'minute_chart': 'ka10080',
        'daily_chart': 'ka10081', 
        'weekly_chart': 'ka10082',
        'monthly_chart': 'ka10083',
        'yearly_chart': 'ka10094'
    }
    
    def get_tick_chart(self, stock_code: str, count: int = 100) -> Dict[str, Any]:
        """
        주식 틱 차트 조회 (ka10079)
        
        Args:
            stock_code: 종목코드
            count: 조회 개수
            
        Returns:
            틱 차트 데이터
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['tick_chart'],
            endpoint='chart',
            params=params,
            method='GET'
        )
    
    def get_minute_chart(
        self,
        stock_code: str,
        interval: int = 1,
        start_date: str = None,
        end_date: str = None,
        count: int = 100
    ) -> Dict[str, Any]:
        """
        주식 분봉 차트 조회 (ka10080)
        
        Args:
            stock_code: 종목코드
            interval: 분봉 간격 (1, 3, 5, 10, 15, 30, 60)
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            count: 조회 개수
            
        Returns:
            분봉 차트 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
            
        # POST 요청용 데이터
        data = {
            "stk_cd": stock_code,
            "tic_scope": str(interval),
            "upd_stkpc_tp": "1",
            "base_dt": end_date,
            "req_cnt": str(count)
        }
        
        if start_date:
            data["start_dt"] = start_date
            
        return self.make_tr_request(
            tr_code=self.TR_CODES['minute_chart'],
            endpoint='chart',
            data=data,
            method='POST'
        )
    
    def get_daily_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None,
        count: int = 100
    ) -> Dict[str, Any]:
        """
        주식 일봉 차트 조회 (ka10081)
        
        Args:
            stock_code: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            count: 조회 개수
            
        Returns:
            일봉 차트 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
            
        data = {
            "stk_cd": stock_code,
            "base_dt": end_date,
            "upd_stkpc_tp": "1",
            "req_cnt": str(count)
        }
        
        if start_date:
            data["start_dt"] = start_date
            
        return self.make_tr_request(
            tr_code=self.TR_CODES['daily_chart'],
            endpoint='chart',
            data=data,
            method='POST'
        )
    
    def get_weekly_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        주식 주봉 차트 조회 (ka10082)
        
        Args:
            stock_code: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            
        Returns:
            주봉 차트 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": "W",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['weekly_chart'],
            endpoint='chart',
            params=params,
            method='GET'
        )
    
    def get_monthly_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        주식 월봉 차트 조회 (ka10083)
        
        Args:
            stock_code: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            
        Returns:
            월봉 차트 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*3)).strftime("%Y%m%d")
            
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": "M",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['monthly_chart'],
            endpoint='chart',
            params=params,
            method='GET'
        )
    
    def get_yearly_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        주식 년봉 차트 조회 (ka10094)
        
        Args:
            stock_code: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            
        Returns:
            년봉 차트 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*10)).strftime("%Y%m%d")
            
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": "Y",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['yearly_chart'],
            endpoint='chart',
            params=params,
            method='GET'
        )
    
    def get_minute_chart_paginated(
        self,
        stock_code: str,
        interval: int = 1,
        start_date: str = None,
        end_date: str = None,
        max_records: int = 1000
    ) -> Dict[str, Any]:
        """
        분봉 차트 대량 조회 (페이지네이션)
        
        Args:
            stock_code: 종목코드
            interval: 분봉 간격
            start_date: 시작일
            end_date: 종료일
            max_records: 최대 조회 개수
            
        Returns:
            통합된 분봉 차트 데이터
        """
        all_data = []
        per_request = 100  # 한 번에 조회할 개수
        current_end_date = end_date or datetime.now().strftime("%Y%m%d")
        
        total_collected = 0
        while total_collected < max_records:
            remaining = min(per_request, max_records - total_collected)
            
            result = self.get_minute_chart(
                stock_code=stock_code,
                interval=interval,
                end_date=current_end_date,
                count=remaining
            )
            
            if not result or result.get('rt_cd') != '0':
                break
                
            # 데이터 추출
            chart_data = result.get('output2', [])
            if not chart_data:
                break
                
            all_data.extend(chart_data)
            total_collected += len(chart_data)
            
            # 시작일 조건 체크
            if start_date:
                last_date = chart_data[-1].get('stck_bsop_date', '')
                if last_date <= start_date:
                    break
                    
            # 다음 페이지를 위한 날짜 업데이트
            if len(chart_data) < remaining:
                # 더 이상 데이터가 없음
                break
                
            # 마지막 데이터의 날짜를 다음 요청의 종료일로 사용
            last_date = chart_data[-1].get('stck_bsop_date', '')
            if last_date == current_end_date:
                # 같은 날짜면 하루 전으로
                last_dt = datetime.strptime(last_date, "%Y%m%d")
                current_end_date = (last_dt - timedelta(days=1)).strftime("%Y%m%d")
            else:
                current_end_date = last_date
                
        # 결과 구성
        if all_data:
            result['output2'] = all_data
            result['total_records'] = len(all_data)
            
        return result