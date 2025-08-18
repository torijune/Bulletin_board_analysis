#!/usr/bin/env python3
"""
주제별 상세 분석 파이프라인
1. 주제별 문서 추출
2. 워드클라우드 생성
3. LLM 상세 분석
4. 리포트 생성
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.utils.config import load_config, ensure_output_dirs
from src.analysis.topic_analysis import TopicAnalysis

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("주제별 상세 분석 파이프라인 시작")
    print("=" * 60)
    
    # 설정 로드
    config = load_config()
    
    # 출력 디렉토리 생성
    output_dir = ensure_output_dirs(config)
    csv_dir = output_dir / "csv"
    
    # 주제별 상세 분석기 초기화
    print("\n1. 주제별 상세 분석기 초기화...")
    topic_analyzer = TopicAnalysis(config)
    
    try:
        # 주제별 상세 분석 실행
        print("\n2. 주제별 상세 분석 시작...")
        results = topic_analyzer.analyze_all_topics(str(csv_dir), str(output_dir))
        
        # 결과 요약 출력
        print(f"\n주제별 상세 분석 완료:")
        print(f"- 분석된 주제 수: {results['total_topics']}개")
        
        # 주제별 통계 출력
        topic_stats = results['topic_stats']
        print(f"\n주제별 통계:")
        for _, topic_stat in topic_stats.iterrows():
            print(f"  주제 {topic_stat['topic_id']} ({topic_stat['topic_name']}):")
            print(f"    - 문서 수: {topic_stat['document_count']}개 ({topic_stat['percentage']}%)")
            print(f"    - 평균 신뢰도: {topic_stat['avg_confidence']}")
            print(f"    - 주요 키워드: {topic_stat['top_keywords']}")
        
        # 생성된 파일들 출력
        print(f"\n생성된 결과물:")
        print(f"- 주제별 통계: {csv_dir}/topic_detailed_statistics.csv")
        print(f"- 주제별 분석: {csv_dir}/topic_analyses.json")
        print(f"- 워드클라우드: {output_dir}/wordclouds/")
        print(f"- 분석 리포트: {output_dir}/reports/topic_analysis_report.md")
        
        # LLM 분석 결과 미리보기
        topic_analyses = results['topic_analyses']
        print(f"\n주제별 LLM 분석 결과 미리보기:")
        for topic_id, analysis in topic_analyses.items():
            print(f"\n  🎯 주제 {topic_id}: {analysis['주제명']}")
            print(f"    📋 요약: {analysis['주제_요약'][:100]}...")
            print(f"    ⚠️  주요 문제점: {', '.join(analysis['주요_문제점'][:2])}")
            print(f"    👥 관련 행위자: {', '.join(analysis['관련_행위자'][:3])}")
            print(f"    💡 해결 방안: {', '.join(analysis['해결_방안'][:2])}")
            print(f"    📊 우선순위: {analysis['우선순위']}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("주제별 상세 분석 파이프라인 완료")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 