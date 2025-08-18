#!/usr/bin/env python3
"""
LLM 분석 파이프라인
1. 클러스터링 결과 로드
2. 대표 문서 선택
3. LLM 분석 수행
4. 결과 저장
"""

import sys
from pathlib import Path
import json

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.utils.config import load_config, ensure_output_dirs
from src.llm.llm_analyzer import LLMAnalyzer
import pandas as pd

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("LLM 분석 파이프라인 시작")
    print("=" * 50)
    
    # 설정 로드
    config = load_config()
    
    # 출력 디렉토리 생성
    output_dir = ensure_output_dirs(config)
    csv_dir = output_dir / "csv"
    
    # 전처리된 데이터 로드
    print("\n1. 데이터 로드 중...")
    try:
        processed_df = pd.read_csv(csv_dir / "preprocessed_data.csv")
        cluster_assignments = pd.read_csv(csv_dir / "cluster_assignments.csv")
        print(f"데이터 로드 완료: {processed_df.shape}")
    except FileNotFoundError as e:
        print(f"필요한 데이터를 찾을 수 없습니다: {e}")
        print("먼저 run_01_data_preprocessing.py와 run_03_clustering.py를 실행해주세요.")
        return False
    
    # LLM 분석기 초기화
    print("\n2. LLM 분석기 초기화...")
    llm_analyzer = LLMAnalyzer(config)
    
    try:
        # 클러스터별 텍스트 수집
        print("\n3. 클러스터별 텍스트 수집 중...")
        cluster_texts = {}
        
        for _, row in cluster_assignments.iterrows():
            cluster_name = row['cluster_name']
            doc_id = row['document_id']
            text = processed_df.iloc[doc_id]['cleaned_text']
            
            if cluster_name not in cluster_texts:
                cluster_texts[cluster_name] = []
            cluster_texts[cluster_name].append(text)
        
        # LLM 분석 수행
        print("\n4. LLM 분석 수행 중...")
        analysis_results = []
        
        for cluster_name, texts in cluster_texts.items():
            print(f"  {cluster_name} 분석 중... ({len(texts)}개 문서)")
            
            # 클러스터 분석
            cluster_analysis = llm_analyzer.analyze_cluster(
                texts, cluster_name, "일반"
            )
            analysis_results.append(cluster_analysis)
        
        # 결과 저장
        print("\n5. 분석 결과 저장 중...")
        llm_analyzer.save_analysis_results(analysis_results, str(csv_dir))
        
        # 결과 요약 출력
        print(f"\nLLM 분석 완료:")
        print(f"- 분석된 클러스터 수: {len(analysis_results)}")
        
        print(f"\n클러스터별 분석 결과:")
        for result in analysis_results:
            cluster_name = result['cluster_name']
            summary = result['cluster_summary']
            
            print(f"  {cluster_name}:")
            print(f"    - 주요 원인: {summary.get('주요_원인', '분석 불가')}")
            print(f"    - 주요 행위자: {summary.get('주요_행위자', '분석 불가')}")
            print(f"    - 공통 요구사항: {summary.get('공통_요구사항', '분석 불가')}")
            print(f"    - 정책 개선점: {summary.get('정책_개선점', '분석 불가')}")
        
        print(f"\n결과 저장 위치:")
        print(f"- CSV 파일: {csv_dir}")
        print(f"- JSON 파일: {csv_dir / 'analysis_results.json'}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("LLM 분석 파이프라인 완료")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 