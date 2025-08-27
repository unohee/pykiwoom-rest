"""
APIResponse 호환성 테스트
기존 dict 동작과의 완전한 호환성 검증
작성일: 2025-01-27
"""

import unittest
import sys
import os

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pykiwoom_rest import APIResponse, KiwoomAPIBase


class TestAPIResponseDictCompatibility(unittest.TestCase):
    """APIResponse의 dict 인터페이스 호환성 테스트"""
    
    def setUp(self):
        """테스트용 응답 데이터 준비"""
        self.test_data = {
            'rt_cd': '0',
            'msg1': 'SUCCESS',
            'output': [
                {'stck_shrn_iscd': '005930', 'stck_prpr': '75000'},
                {'stck_shrn_iscd': '000660', 'stck_prpr': '45000'}
            ],
            'output1': {'total_count': '2'},
            'output2': [{'summary': 'test'}]
        }
        self.api_response = APIResponse.create_success(
            data=self.test_data,
            tr_code='ka10001',
            endpoint='stock_info'
        )
    
    def test_dict_getitem_access(self):
        """Dict 스타일 키 접근"""
        self.assertEqual(self.api_response['rt_cd'], '0')
        self.assertEqual(self.api_response['msg1'], 'SUCCESS')
        self.assertEqual(len(self.api_response['output']), 2)
        
        with self.assertRaises(KeyError):
            _ = self.api_response['nonexistent_key']
    
    def test_dict_contains(self):
        """'in' 연산자 테스트"""
        self.assertTrue('rt_cd' in self.api_response)
        self.assertTrue('output' in self.api_response)
        self.assertFalse('nonexistent_key' in self.api_response)
    
    def test_dict_get_method(self):
        """dict.get() 메서드 호환성"""
        self.assertEqual(self.api_response.get('rt_cd'), '0')
        self.assertEqual(self.api_response.get('msg1'), 'SUCCESS')
        self.assertIsNone(self.api_response.get('nonexistent_key'))
        self.assertEqual(self.api_response.get('nonexistent_key', 'default'), 'default')
    
    def test_dict_keys_values_items(self):
        """keys(), values(), items() 메서드"""
        keys = list(self.api_response.keys())
        self.assertIn('rt_cd', keys)
        self.assertIn('output', keys)
        
        values = list(self.api_response.values())
        self.assertIn('0', values)
        
        items = list(self.api_response.items())
        self.assertIn(('rt_cd', '0'), items)
    
    def test_dict_iteration(self):
        """반복자 지원"""
        keys_from_iteration = []
        for key in self.api_response:
            keys_from_iteration.append(key)
        
        self.assertIn('rt_cd', keys_from_iteration)
        self.assertIn('output', keys_from_iteration)
    
    def test_dict_len(self):
        """len() 지원"""
        self.assertEqual(len(self.api_response), len(self.test_data))
    
    def test_dict_update(self):
        """update() 메서드"""
        self.api_response.update({'new_key': 'new_value'})
        self.assertEqual(self.api_response['new_key'], 'new_value')
    
    def test_bool_evaluation(self):
        """Boolean 평가 (성공/실패 기준)"""
        success_response = APIResponse.create_success({'test': 'data'})
        error_response = APIResponse.create_error('Test error')
        
        self.assertTrue(success_response)
        self.assertFalse(error_response)
    
    def test_legacy_dict_conversion(self):
        """기존 dict 형태로 변환"""
        legacy_dict = self.api_response.to_legacy_dict()
        self.assertIsInstance(legacy_dict, dict)
        self.assertEqual(legacy_dict['rt_cd'], '0')
        self.assertEqual(legacy_dict['output'], self.test_data['output'])


class TestAPIResponseMetadata(unittest.TestCase):
    """APIResponse 메타데이터 기능 테스트"""
    
    def test_metadata_presence(self):
        """메타데이터 존재 확인"""
        response = APIResponse.create_success(
            data={'test': 'data'},
            tr_code='ka10001',
            endpoint='stock_info'
        )
        
        metadata = response.metadata
        self.assertIn('timestamp', metadata)
        self.assertIn('request_id', metadata)
        self.assertEqual(metadata['tr_code'], 'ka10001')
        self.assertEqual(metadata['endpoint'], 'stock_info')
    
    def test_error_response_structure(self):
        """에러 응답 구조 확인"""
        error_response = APIResponse.create_error(
            error_message='Test error',
            error_code='E001',
            error_details={'detail1': 'value1'},
            tr_code='ka10001'
        )
        
        self.assertFalse(error_response.success)
        self.assertIsNotNone(error_response.error)
        self.assertEqual(error_response.error['message'], 'Test error')
        self.assertEqual(error_response.error['code'], 'E001')
        self.assertEqual(error_response.error['details']['detail1'], 'value1')


class TestKiwoomSpecificMethods(unittest.TestCase):
    """키움 API 특화 메서드 테스트"""
    
    def test_kiwoom_success_check(self):
        """키움 API 성공 여부 확인"""
        success_response = APIResponse.create_success({'rt_cd': '0', 'msg1': 'SUCCESS'})
        error_response = APIResponse.create_success({'rt_cd': '1', 'msg1': 'ERROR'})
        
        self.assertTrue(success_response.is_kiwoom_success())
        self.assertFalse(error_response.is_kiwoom_success())
    
    def test_kiwoom_message_extraction(self):
        """키움 API 메시지 추출"""
        response = APIResponse.create_success({'rt_cd': '0', 'msg1': 'SUCCESS'})
        self.assertEqual(response.get_kiwoom_message(), 'SUCCESS')
    
    def test_output_data_access(self):
        """출력 데이터 접근"""
        response = APIResponse.create_success({
            'rt_cd': '0',
            'output': [{'test': 'data'}],
            'output1': {'count': '1'}
        })
        
        self.assertTrue(response.has_output_data('output'))
        self.assertTrue(response.has_output_data('output1'))
        self.assertFalse(response.has_output_data('output2'))
        
        output_data = response.get_output_data('output')
        self.assertEqual(output_data, [{'test': 'data'}])


class TestBackwardCompatibility(unittest.TestCase):
    """하위 호환성 종합 테스트"""
    
    def test_existing_code_patterns(self):
        """기존 코드 패턴 호환성"""
        # 기존 코드에서 자주 사용되는 패턴들
        response = APIResponse.create_success({
            'rt_cd': '0',
            'msg1': 'SUCCESS',
            'output': [{'stck_shrn_iscd': '005930', 'stck_prpr': '75000'}]
        })
        
        # 패턴 1: rt_cd 체크
        self.assertEqual(response['rt_cd'], '0')
        self.assertEqual(response.get('rt_cd'), '0')
        
        # 패턴 2: 조건부 처리
        if response['rt_cd'] == '0':
            data = response['output']
            self.assertEqual(len(data), 1)
        
        # 패턴 3: 키 존재 확인
        if 'output' in response:
            self.assertTrue(True)
        
        # 패턴 4: 기본값을 가진 접근
        msg = response.get('msg1', 'No message')
        self.assertEqual(msg, 'SUCCESS')
        
        # 패턴 5: 반복 처리
        keys = []
        for key in response:
            keys.append(key)
        self.assertIn('rt_cd', keys)


if __name__ == '__main__':
    unittest.main()