#!/usr/bin/env python3
"""
대규모 상담/게시판 데이터 주제 발견 및 심층 분석 파이프라인
모든 단계를 순차적으로 실행합니다.
"""

import sys
import subprocess
from pathlib import Path
import argparse

def run_pipeline(steps=None, skip_topic_analysis=False):
    """전체 파이프라인을 실행합니다."""
    print("=" * 60)
    print("대규모 상담/게시판 데이터 주제 발견 및 심층 분석")
    print("전체 파이프라인 실행")
    print("=" * 60)
    
    # 실행할 스크립트 목록
    all_scripts = [
        ("데이터 전처리", "run_01_data_preprocessing.py"),
        ("주제 발견", "run_02_topic_discovery.py"), 
        ("클러스터링", "run_03_clustering.py"),
        ("LLM 분석", "run_04_llm_analysis.py"),
        ("리포트 생성", "run_05_report_generation.py")
    ]
    
    # 주제별 상세 분석 (선택적)
    if not skip_topic_analysis:
        all_scripts.append(("주제별 상세 분석", "run_topic_analysis.py"))
    
    # 특정 단계만 실행할 경우
    if steps:
        selected_scripts = []
        for step_name, script_name in all_scripts:
            if any(step in step_name.lower() for step in steps):
                selected_scripts.append((step_name, script_name))
        all_scripts = selected_scripts
    
    print(f"실행할 단계: {len(all_scripts)}개")
    for i, (step_name, script_name) in enumerate(all_scripts, 1):
        print(f"  {i}. {step_name}: {script_name}")
    
    print("\n" + "=" * 60)
    
    for i, (step_name, script_name) in enumerate(all_scripts, 1):
        print(f"\n{'='*20} 단계 {i}: {step_name} {'='*20}")
        
        try:
            # 스크립트 실행
            result = subprocess.run([sys.executable, script_name], 
                                  capture_output=False, 
                                  text=True)
            
            if result.returncode != 0:
                print(f"❌ {script_name} 실행 실패")
                print("이전 단계에서 오류가 발생했습니다. 수동으로 확인해주세요.")
                return False
            else:
                print(f"✅ {script_name} 실행 완료")
                
        except Exception as e:
            print(f"❌ {script_name} 실행 중 오류 발생: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("🎉 전체 파이프라인 실행 완료!")
    print("=" * 60)
    print("\n📁 결과물 위치:")
    print("- CSV 파일: outputs/csv/")
    print("- 리포트: outputs/reports/")
    print("- 시각화: outputs/visualizations/")
    print("- 워드클라우드: outputs/wordclouds/")
    print("\n📋 주요 결과물:")
    print("- global_topics_top_terms.csv: 주제별 키워드")
    print("- topic_assignments.csv: 문서별 주제 할당")
    print("- cluster_summary.csv: 클러스터별 요약")
    print("- analysis_results.json: LLM 분석 결과")
    print("- topic_analyses.json: 주제별 상세 분석")
    print("- 분석_리포트.md: 최종 분석 리포트")
    print("- topic_analysis_report.md: 주제별 분석 리포트")
    
    return True

def run_individual_step(step_name):
    """개별 단계를 실행합니다."""
    step_scripts = {
        "preprocessing": "run_01_data_preprocessing.py",
        "topic": "run_02_topic_discovery.py",
        "clustering": "run_03_clustering.py",
        "llm": "run_04_llm_analysis.py",
        "report": "run_05_report_generation.py",
        "topic-analysis": "run_topic_analysis.py"
    }
    
    if step_name not in step_scripts:
        print(f"❌ 알 수 없는 단계: {step_name}")
        print(f"사용 가능한 단계: {', '.join(step_scripts.keys())}")
        return False
    
    script_name = step_scripts[step_name]
    print(f"실행 중: {script_name}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode != 0:
            print(f"❌ {script_name} 실행 실패")
            return False
        else:
            print(f"✅ {script_name} 실행 완료")
            return True
            
    except Exception as e:
        print(f"❌ {script_name} 실행 중 오류 발생: {e}")
        return False

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="상담 데이터 분석 파이프라인")
    parser.add_argument("--steps", nargs="+", 
                       help="실행할 특정 단계들 (preprocessing, topic, clustering, llm, report, topic-analysis)")
    parser.add_argument("--step", type=str,
                       help="개별 단계 실행")
    parser.add_argument("--skip-topic-analysis", action="store_true",
                       help="주제별 상세 분석 단계 건너뛰기")
    
    args = parser.parse_args()
    
    if args.step:
        # 개별 단계 실행
        success = run_individual_step(args.step)
    else:
        # 전체 파이프라인 또는 특정 단계들 실행
        success = run_pipeline(args.steps, args.skip_topic_analysis)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 