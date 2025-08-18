#!/usr/bin/env python3
"""
전체 분석 파이프라인 실행 스크립트
모든 단계를 순차적으로 실행합니다.
"""

import sys
import subprocess
from pathlib import Path

def run_pipeline():
    """전체 파이프라인을 실행합니다."""
    print("=" * 60)
    print("대규모 상담/게시판 데이터 주제 발견 및 심층 분석")
    print("전체 파이프라인 실행")
    print("=" * 60)
    
    # 실행할 스크립트 목록
    scripts = [
        "run_01_data_preprocessing.py",
        "run_02_topic_discovery.py", 
        "run_03_clustering.py",
        "run_04_llm_analysis.py",
        "run_05_report_generation.py"
    ]
    
    for i, script in enumerate(scripts, 1):
        print(f"\n{'='*20} 단계 {i}: {script} {'='*20}")
        
        try:
            # 스크립트 실행
            result = subprocess.run([sys.executable, script], 
                                  capture_output=False, 
                                  text=True)
            
            if result.returncode != 0:
                print(f"❌ {script} 실행 실패")
                print("이전 단계에서 오류가 발생했습니다. 수동으로 확인해주세요.")
                return False
            else:
                print(f"✅ {script} 실행 완료")
                
        except Exception as e:
            print(f"❌ {script} 실행 중 오류 발생: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("🎉 전체 파이프라인 실행 완료!")
    print("=" * 60)
    print("\n📁 결과물 위치:")
    print("- CSV 파일: outputs/csv/")
    print("- 리포트: outputs/reports/")
    print("- 시각화: outputs/visualizations/")
    print("\n📋 주요 결과물:")
    print("- global_topics_top_terms.csv: 주제별 키워드")
    print("- topic_assignments.csv: 문서별 주제 할당")
    print("- cluster_summary.csv: 클러스터별 요약")
    print("- 분석_리포트.md: 최종 분석 리포트")
    
    return True

if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1) 