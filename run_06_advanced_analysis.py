#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
고급 분석 파이프라인
- N-gram 분석
- 상담인 유형별 교차 분석  
- 정책 인사이트 도출
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from pathlib import Path
import json

from src.utils.config import load_config, ensure_output_dirs
from src.utils.text_processing import analyze_ngrams
from src.analysis.cross_analysis import CrossAnalysis
from src.analysis.policy_insights import PolicyInsights

def main():
    """고급 분석 파이프라인 메인 함수"""
    print("=" * 50)
    print("고급 분석 파이프라인 시작")
    print("=" * 50)
    
    # 1. 설정 로드
    print("\n1. 설정 로드 중...")
    config = load_config()
    ensure_output_dirs(config)
    
    # 2. 전처리된 데이터 로드
    print("\n2. 전처리된 데이터 로드 중...")
    preprocessed_data_path = Path(config['data']['output_dir']) / "csv" / "preprocessed_data.csv"
    
    if not preprocessed_data_path.exists():
        print("전처리된 데이터를 찾을 수 없습니다. 먼저 run_01_data_preprocessing.py를 실행해주세요.")
        return
    
    df = pd.read_csv(preprocessed_data_path)
    print(f"데이터 로드 완료: {df.shape}")
    
    # 3. 주제 발견 결과 로드
    print("\n3. 주제 발견 결과 로드 중...")
    topic_results = {}
    topic_terms_path = Path(config['data']['output_dir']) / "csv" / "global_topics_top_terms.csv"
    
    if topic_terms_path.exists():
        topic_terms_df = pd.read_csv(topic_terms_path)
        topic_results['top_terms'] = {}
        
        for topic_id in topic_terms_df['topic_id'].unique():
            topic_terms = topic_terms_df[topic_terms_df['topic_id'] == topic_id]
            terms = [(row['term'], row['score']) for _, row in topic_terms.iterrows()]
            topic_results['top_terms'][topic_id] = terms
    
    # 4. 클러스터링 결과 로드
    print("\n4. 클러스터링 결과 로드 중...")
    cluster_results = {}
    cluster_summary_path = Path(config['data']['output_dir']) / "csv" / "cluster_summary.csv"
    
    if cluster_summary_path.exists():
        cluster_results['cluster_stats'] = pd.read_csv(cluster_summary_path)
    
    # 5. N-gram 분석
    print("\n5. N-gram 분석 중...")
    texts = df['combined_text'].tolist()
    
    # 2-gram 분석
    bigram_results = analyze_ngrams(texts, n=2, min_freq=1)
    
    # 3-gram 분석
    trigram_results = analyze_ngrams(texts, n=3, min_freq=1)
    
    # N-gram 결과 저장
    output_dir = Path(config['data']['output_dir']) / "csv"
    
    # 2-gram 결과 저장
    bigram_df = pd.DataFrame(bigram_results['2-gram'], columns=['bigram', 'frequency'])
    bigram_df.to_csv(output_dir / "bigram_analysis.csv", index=False, encoding='utf-8-sig')
    
    # 3-gram 결과 저장
    trigram_df = pd.DataFrame(trigram_results['3-gram'], columns=['trigram', 'frequency'])
    trigram_df.to_csv(output_dir / "trigram_analysis.csv", index=False, encoding='utf-8-sig')
    
    print(f"N-gram 분석 완료:")
    print(f"  2-gram: {len(bigram_results['2-gram'])}개")
    print(f"  3-gram: {len(trigram_results['3-gram'])}개")
    
    # 6. 상담인 유형별 교차 분석
    print("\n6. 상담인 유형별 교차 분석 중...")
    cross_analyzer = CrossAnalysis(config)
    cross_results = cross_analyzer.analyze_consultation_patterns(df, str(output_dir))
    
    print("교차 분석 완료")
    
    # 7. 정책 인사이트 도출
    print("\n7. 정책 인사이트 도출 중...")
    policy_analyzer = PolicyInsights(config)
    policy_results = policy_analyzer.generate_policy_insights(
        df, topic_results, cluster_results, str(output_dir)
    )
    
    print("정책 인사이트 도출 완료")
    
    # 8. 최종 결과 요약
    print("\n8. 최종 결과 요약...")
    
    print(f"\n📊 N-gram 분석 결과:")
    print(f"  주요 2-gram (상위 5개):")
    for i, (bigram, freq) in enumerate(bigram_results['2-gram'][:5], 1):
        print(f"    {i}. {bigram}: {freq}회")
    
    print(f"\n  주요 3-gram (상위 5개):")
    for i, (trigram, freq) in enumerate(trigram_results['3-gram'][:5], 1):
        print(f"    {i}. {trigram}: {freq}회")
    
    print(f"\n📈 교차 분석 결과:")
    print(f"  상담인 유형별 빈도:")
    for person_type, count in cross_results['person_type_freq'].items():
        print(f"    {person_type}: {count}건")
    
    print(f"\n  주요 패턴:")
    for pattern in cross_results['insights']['key_patterns']:
        print(f"    {pattern['person_type']} → {pattern['main_consultation']}: {pattern['count']}건")
    
    print(f"\n💡 정책 인사이트:")
    print(f"  FAQ 제안: {len(policy_results['faq_suggestions'])}개")
    print(f"  교육자료 제안: {len(policy_results['education_materials'])}개")
    print(f"  규약 개선 제안: {len(policy_results['regulation_improvements'])}개")
    print(f"  리스크 관리: {len(policy_results['risk_management'])}개")
    print(f"  우선순위 액션: {len(policy_results['priority_actions'])}개")
    
    print(f"\n📁 결과 저장 위치:")
    print(f"  CSV 파일: {output_dir}")
    print(f"  시각화: {Path(config['data']['output_dir']) / 'visualizations'}")
    print(f"  정책 인사이트: {output_dir / 'policy_insights.json'}")
    
    print("\n" + "=" * 50)
    print("고급 분석 파이프라인 완료")
    print("=" * 50)

if __name__ == "__main__":
    main() 