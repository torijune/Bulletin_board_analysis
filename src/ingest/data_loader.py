import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from ..utils.config import load_config
from ..utils.text_processing import clean_text, combine_text_columns, filter_by_length, remove_duplicates

class DataLoader:
    """데이터 로딩 및 전처리 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_config = config['data']
        self.preprocessing_config = config['preprocessing']
        
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """Excel/CSV 파일을 로드합니다."""
        if file_path is None:
            file_path = self.data_config['input_file']
        
        file_path = Path(file_path)
        
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {file_path.suffix}")
        
        print(f"데이터 로드 완료: {df.shape}")
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터를 전처리합니다."""
        print("데이터 전처리 시작...")
        
        # 헤더가 없는 경우 처리
        if df.columns.str.contains('Unnamed').any():
            df = self._fix_header(df)
        
        # 텍스트 컬럼 결합
        text_columns = self.preprocessing_config['text_columns']
        if text_columns:
            df['combined_text'] = combine_text_columns(df, text_columns)
        else:
            # 기본 컬럼 사용
            content_col = self.data_config['columns']['content']
            summary_col = self.data_config['columns']['summary']
            df['combined_text'] = combine_text_columns(df, [summary_col, content_col])
        
        # 텍스트 정리
        df['cleaned_text'] = df['combined_text'].apply(clean_text)
        
        # 최소 길이 필터링
        min_length = self.preprocessing_config['min_text_length']
        df = df[df['cleaned_text'].str.len() >= min_length].copy()
        
        # 중복 제거
        if self.preprocessing_config['remove_duplicates']:
            df = remove_duplicates(df, 'cleaned_text')
        
        # 인덱스 재설정
        df = df.reset_index(drop=True)
        
        print(f"전처리 완료: {df.shape}")
        return df
    
    def _fix_header(self, df: pd.DataFrame) -> pd.DataFrame:
        """헤더가 없는 경우 헤더를 찾아 설정합니다."""
        # 실제 헤더 행 찾기
        for idx, row in df.iterrows():
            if '연번' in row.values or '상담일자' in row.values:
                # 헤더 행을 찾았으므로 해당 행을 헤더로 설정
                df.columns = df.iloc[idx]
                df = df.iloc[idx+1:].reset_index(drop=True)
                break
        
        return df
    
    def get_sample_data(self) -> pd.DataFrame:
        """샘플 데이터를 생성합니다 (테스트용)."""
        sample_data = {
            '연번': range(1, 101),
            '상담일자': ['2025.1.2-3'] * 100,
            '상담유형': ['전화'] * 100,
            '상담요약': ['분쟁', '기타', '관리비', '관리규약', '의결권'] * 20,
            '상담인 유형': ['관리소장', '점유자', '구분소유자', '기타'] * 25,
            '상담내용': [
                '총회시 위임장에 소유자가 직접 서명을 하여야 하는지 문의',
                '부당한 관리비 인상을 일방적 요구에 응해야 하는지 문의',
                '관리규약 제정 관련 문의',
                '집회 결의에 관한 문의',
                '회계감사 대상에 해당이 되는지 문의'
            ] * 20
        }
        
        return pd.DataFrame(sample_data) 