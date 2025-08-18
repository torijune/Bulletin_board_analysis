#!/usr/bin/env python3
"""
주제 발견 파이프라인
1. 전처리된 데이터 로드
2. 주제 발견 (LDA)
3. 결과 저장 및 시각화
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.utils.config import load_config, ensure_output_dirs
from src.topics.topic_discovery import TopicDiscovery
import pandas as pd

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("주제 발견 파이프라인 시작")
    print("=" * 50)
    
    # 설정 로드
    config = load_config()
    
    # 출력 디렉토리 생성
    output_dir = ensure_output_dirs(config)
    csv_dir = output_dir / "csv"
    
    # 전처리된 데이터 로드
    print("\n1. 전처리된 데이터 로드 중...")
    try:
        processed_df = pd.read_csv(csv_dir / "preprocessed_data.csv")
        print(f"데이터 로드 완료: {processed_df.shape}")
    except FileNotFoundError:
        print("전처리된 데이터를 찾을 수 없습니다. 먼저 run_01_data_preprocessing.py를 실행해주세요.")
        return False
    
    # 주제 발견 모델 초기화
    print("\n2. 주제 발견 모델 초기화...")
    topic_discovery = TopicDiscovery(config)
    
    try:
        # 텍스트 추출
        texts = processed_df['cleaned_text'].tolist()
        
        # 주제 발견 모델 학습
        print("\n3. 주제 발견 모델 학습 중...")
        topic_discovery.fit(texts)
        
        # 주제별 상위 단어 추출
        print("\n4. 주제별 상위 단어 추출 중...")
        top_terms = topic_discovery.get_top_terms()
        
        # 주제 할당
        print("\n5. 문서별 주제 할당 중...")
        topic_assignments, confidence_scores = topic_discovery.assign_topics(texts)
        
        # 결과 저장
        print("\n6. 결과 저장 중...")
        topic_discovery.save_results(texts, str(csv_dir))
        
        # 시각화 생성
        print("\n7. 시각화 생성 중...")
        topic_discovery.visualize_topics(str(output_dir / "visualizations"))
        
        # 결과 요약 출력
        print(f"\n주제 발견 완료:")
        print(f"- 발견된 주제 수: {len(top_terms)}")
        print(f"- 분석된 문서 수: {len(texts)}")
        
        print("\n주제별 상위 키워드:")
        for topic_id, terms in top_terms.items():
            top_keywords = [term for term, _ in terms[:5]]
            print(f"  주제 {topic_id+1}: {', '.join(top_keywords)}")
        
        # 주제별 문서 수 통계
        topic_counts = pd.Series(topic_assignments).value_counts().sort_index()
        print(f"\n주제별 문서 수:")
        for topic_id, count in topic_counts.items():
            print(f"  주제 {topic_id+1}: {count}개")
        
        print(f"\n결과 저장 위치:")
        print(f"- CSV 파일: {csv_dir}")
        print(f"- 시각화: {output_dir / 'visualizations'}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("주제 발견 파이프라인 완료")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 