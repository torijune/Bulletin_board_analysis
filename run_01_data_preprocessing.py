#!/usr/bin/env python3
"""
데이터 전처리 파이프라인
1. 데이터 로드
2. 전처리
3. 결과 저장
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.utils.config import load_config, ensure_output_dirs
from src.ingest.data_loader import DataLoader

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("데이터 전처리 파이프라인 시작")
    print("=" * 50)
    
    # 설정 로드
    config = load_config()
    
    # 출력 디렉토리 생성
    output_dir = ensure_output_dirs(config)
    
    # 데이터 로더 초기화
    data_loader = DataLoader(config)
    
    try:
        # 데이터 로드
        print("\n1. 데이터 로드 중...")
        df = data_loader.load_data()
        
        # 데이터 전처리
        print("\n2. 데이터 전처리 중...")
        processed_df = data_loader.preprocess_data(df)
        
        # 전처리된 데이터 저장
        print("\n3. 전처리된 데이터 저장 중...")
        processed_df.to_csv(output_dir / "csv" / "preprocessed_data.csv", 
                           index=False, encoding='utf-8-sig')
        
        # 전처리 통계 출력
        print(f"\n전처리 완료:")
        print(f"- 원본 데이터: {df.shape}")
        print(f"- 전처리 후 데이터: {processed_df.shape}")
        print(f"- 제거된 행: {len(df) - len(processed_df)}")
        
        # 텍스트 길이 통계
        text_lengths = processed_df['cleaned_text'].str.len()
        print(f"- 평균 텍스트 길이: {text_lengths.mean():.1f}")
        print(f"- 최소 텍스트 길이: {text_lengths.min()}")
        print(f"- 최대 텍스트 길이: {text_lengths.max()}")
        
        print(f"\n전처리된 데이터 저장 위치: {output_dir / 'csv' / 'preprocessed_data.csv'}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("데이터 전처리 파이프라인 완료")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 