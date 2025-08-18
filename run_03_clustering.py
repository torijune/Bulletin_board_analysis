#!/usr/bin/env python3
"""
클러스터링 파이프라인
1. 전처리된 데이터 로드
2. 임베딩 생성
3. 클러스터링 수행
4. 결과 저장 및 시각화
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.utils.config import load_config, ensure_output_dirs
from src.cluster.document_clustering import DocumentClustering
import pandas as pd

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("클러스터링 파이프라인 시작")
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
    
    # 클러스터링 모델 초기화
    print("\n2. 클러스터링 모델 초기화...")
    clustering = DocumentClustering(config)
    
    try:
        # 텍스트 추출
        texts = processed_df['cleaned_text'].tolist()
        
        # 클러스터링 수행
        print("\n3. 클러스터링 수행 중...")
        cluster_results = clustering.cluster_documents(texts)
        
        # 결과 저장
        print("\n4. 클러스터링 결과 저장 중...")
        clustering.save_cluster_results(cluster_results, str(csv_dir))
        
        # 시각화 생성
        print("\n5. 시각화 생성 중...")
        clustering.visualize_clusters(cluster_results, str(output_dir / "visualizations"))
        
        # 결과 요약 출력
        print(f"\n클러스터링 완료:")
        print(f"- 생성된 클러스터 수: {cluster_results['optimal_k']}")
        print(f"- 분석된 문서 수: {len(texts)}")
        
        # 클러스터별 통계
        cluster_stats = cluster_results['cluster_stats']
        print(f"\n클러스터별 문서 수:")
        for _, cluster in cluster_stats.iterrows():
            print(f"  {cluster['cluster_name']}: {cluster['document_count']}개")
        
        # 대표 문서 예시
        print(f"\n클러스터별 대표 문서:")
        for _, cluster in cluster_stats.iterrows():
            print(f"  {cluster['cluster_name']}: {cluster['representative_text'][:50]}...")
        
        print(f"\n결과 저장 위치:")
        print(f"- CSV 파일: {csv_dir}")
        print(f"- 시각화: {output_dir / 'visualizations'}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("클러스터링 파이프라인 완료")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 