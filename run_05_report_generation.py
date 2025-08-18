#!/usr/bin/env python3
"""
리포트 생성 파이프라인
1. 모든 분석 결과 로드
2. 마크다운 리포트 생성
3. 시각화 생성
4. 최종 결과 통합
"""

import sys
from pathlib import Path
import json

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.utils.config import load_config, ensure_output_dirs
from src.report.report_generator import ReportGenerator
import pandas as pd

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("리포트 생성 파이프라인 시작")
    print("=" * 50)
    
    # 설정 로드
    config = load_config()
    
    # 출력 디렉토리 생성
    output_dir = ensure_output_dirs(config)
    csv_dir = output_dir / "csv"
    reports_dir = output_dir / "reports"
    
    # 분석 결과 로드
    print("\n1. 분석 결과 로드 중...")
    try:
        # 전처리된 데이터
        processed_df = pd.read_csv(csv_dir / "preprocessed_data.csv")
        texts = processed_df['cleaned_text'].tolist()
        
        # 주제 발견 결과
        topic_assignments = pd.read_csv(csv_dir / "topic_assignments.csv")
        topic_summary = pd.read_csv(csv_dir / "topic_summary.csv")
        
        # 클러스터링 결과
        cluster_assignments = pd.read_csv(csv_dir / "cluster_assignments.csv")
        cluster_summary = pd.read_csv(csv_dir / "cluster_summary.csv")
        
        # LLM 분석 결과
        with open(csv_dir / "analysis_results.json", 'r', encoding='utf-8') as f:
            analysis_results = json.load(f)
        
        print("모든 분석 결과 로드 완료")
        
    except FileNotFoundError as e:
        print(f"필요한 분석 결과를 찾을 수 없습니다: {e}")
        print("먼저 이전 파이프라인들을 실행해주세요.")
        return False
    
    # 리포트 생성기 초기화
    print("\n2. 리포트 생성기 초기화...")
    report_generator = ReportGenerator(config)
    
    try:
        # 주제 발견 결과 준비
        print("\n3. 주제 발견 결과 준비 중...")
        topic_results = {
            'top_terms': {},
            'topic_assignments': topic_assignments,
            'topic_summary': topic_summary
        }
        
        # 주제별 상위 단어 로드
        top_terms_df = pd.read_csv(csv_dir / "global_topics_top_terms.csv")
        for topic_id in top_terms_df['topic_id'].unique():
            topic_terms = top_terms_df[top_terms_df['topic_id'] == topic_id]
            topic_results['top_terms'][topic_id] = [
                (row['term'], row['score']) 
                for _, row in topic_terms.iterrows()
            ]
        
        # 클러스터링 결과 준비
        print("\n4. 클러스터링 결과 준비 중...")
        cluster_results = {
            'cluster_stats': cluster_summary,
            'cluster_assignments': cluster_assignments
        }
        
        # 마크다운 리포트 생성
        print("\n5. 마크다운 리포트 생성 중...")
        report_generator.generate_markdown_report(
            topic_results, cluster_results, analysis_results, str(reports_dir)
        )
        
        # 시각화 생성
        print("\n6. 시각화 생성 중...")
        report_generator.generate_all_visualizations(
            topic_results, cluster_results, texts, str(output_dir)
        )
        
        # 최종 통계 생성
        print("\n7. 최종 통계 생성 중...")
        final_stats = {
            'total_documents': len(texts),
            'total_topics': len(topic_results['top_terms']),
            'total_clusters': len(cluster_results['cluster_stats']),
            'analysis_summary': {}
        }
        
        # 분석 결과 요약
        for result in analysis_results:
            cluster_name = result['cluster_name']
            summary = result['cluster_summary']
            final_stats['analysis_summary'][cluster_name] = {
                'document_count': len(result['individual_analyses']),
                'main_cause': summary.get('주요_원인', '분석 불가'),
                'policy_improvement': summary.get('정책_개선점', '분석 불가')
            }
        
        # 통계 저장
        with open(reports_dir / "final_statistics.json", 'w', encoding='utf-8') as f:
            json.dump(final_stats, f, ensure_ascii=False, indent=2)
        
        # 결과 요약 출력
        print(f"\n리포트 생성 완료:")
        print(f"- 총 문서 수: {final_stats['total_documents']}")
        print(f"- 발견된 주제 수: {final_stats['total_topics']}")
        print(f"- 생성된 클러스터 수: {final_stats['total_clusters']}")
        
        print(f"\n주요 정책 개선점:")
        for cluster_name, stats in final_stats['analysis_summary'].items():
            print(f"  {cluster_name}: {stats['policy_improvement']}")
        
        print(f"\n결과 저장 위치:")
        print(f"- 마크다운 리포트: {reports_dir / '분석_리포트.md'}")
        print(f"- 시각화: {output_dir / 'visualizations'}")
        print(f"- 통계: {reports_dir / 'final_statistics.json'}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("리포트 생성 파이프라인 완료")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 