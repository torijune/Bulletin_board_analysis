#!/usr/bin/env python3
"""
체크 및 테스트 유틸리티 함수들
데이터 검증, 결과 확인, 성능 테스트 등의 기능을 제공합니다.
"""

import pandas as pd
import json
import os
from pathlib import Path
from typing import Dict, Any, List

def check_data_integrity(data_path: str) -> Dict[str, Any]:
    """데이터 무결성을 검사합니다."""
    print("데이터 무결성 검사 중...")
    
    try:
        df = pd.read_excel(data_path)
        
        # 기본 정보
        info = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'column_names': df.columns.tolist(),
            'data_types': df.dtypes.to_dict()
        }
        
        # 필수 컬럼 확인
        required_columns = ['연번', '상담일자', '상담유형', '상담요약', '상담인 유형', '상담내용']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        info['missing_required_columns'] = missing_columns
        info['data_valid'] = len(missing_columns) == 0
        
        print(f"데이터 검사 완료: {info['total_rows']}행, {info['total_columns']}열")
        return info
        
    except Exception as e:
        print(f"데이터 검사 실패: {e}")
        return {'error': str(e), 'data_valid': False}

def check_topic_results(output_dir: str) -> Dict[str, Any]:
    """주제 발견 결과를 확인합니다."""
    print("주제 발견 결과 확인 중...")
    
    results = {}
    
    # 파일 존재 확인
    files_to_check = [
        'topic_assignments.csv',
        'global_topics_top_terms.csv',
        'topic_summary.csv'
    ]
    
    for file_name in files_to_check:
        file_path = Path(output_dir) / 'csv' / file_name
        results[file_name] = file_path.exists()
        
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                results[f"{file_name}_rows"] = len(df)
            except Exception as e:
                results[f"{file_name}_error"] = str(e)
    
    # 주제별 문서 수 확인
    if results.get('topic_assignments.csv'):
        try:
            assignments = pd.read_csv(Path(output_dir) / 'csv' / 'topic_assignments.csv')
            topic_counts = assignments['topic_id'].value_counts().to_dict()
            results['topic_distribution'] = topic_counts
            results['total_topics'] = len(topic_counts)
        except Exception as e:
            results['topic_distribution_error'] = str(e)
    
    print(f"주제 발견 결과 확인 완료: {results.get('total_topics', 0)}개 주제")
    return results

def check_clustering_results(output_dir: str) -> Dict[str, Any]:
    """클러스터링 결과를 확인합니다."""
    print("클러스터링 결과 확인 중...")
    
    results = {}
    
    # 파일 존재 확인
    files_to_check = [
        'cluster_assignments.csv',
        'cluster_summary.csv'
    ]
    
    for file_name in files_to_check:
        file_path = Path(output_dir) / 'csv' / file_name
        results[file_name] = file_path.exists()
        
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                results[f"{file_name}_rows"] = len(df)
            except Exception as e:
                results[f"{file_name}_error"] = str(e)
    
    # 클러스터별 문서 수 확인
    if results.get('cluster_assignments.csv'):
        try:
            assignments = pd.read_csv(Path(output_dir) / 'csv' / 'cluster_assignments.csv')
            cluster_counts = assignments['cluster_name'].value_counts().to_dict()
            results['cluster_distribution'] = cluster_counts
            results['total_clusters'] = len(cluster_counts)
        except Exception as e:
            results['cluster_distribution_error'] = str(e)
    
    print(f"클러스터링 결과 확인 완료: {results.get('total_clusters', 0)}개 클러스터")
    return results

def check_llm_analysis_results(output_dir: str) -> Dict[str, Any]:
    """LLM 분석 결과를 확인합니다."""
    print("LLM 분석 결과 확인 중...")
    
    results = {}
    
    # 파일 존재 확인
    files_to_check = [
        'analysis_results.json',
        'individual_analyses.csv',
        'cluster_analyses.csv'
    ]
    
    for file_name in files_to_check:
        file_path = Path(output_dir) / 'csv' / file_name
        results[file_name] = file_path.exists()
        
        if file_path.exists():
            try:
                if file_name.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    results[f"{file_name}_items"] = len(data) if isinstance(data, list) else 1
                else:
                    df = pd.read_csv(file_path)
                    results[f"{file_name}_rows"] = len(df)
            except Exception as e:
                results[f"{file_name}_error"] = str(e)
    
    print("LLM 분석 결과 확인 완료")
    return results

def check_topic_analysis_results(output_dir: str) -> Dict[str, Any]:
    """주제별 분석 결과를 확인합니다."""
    print("주제별 분석 결과 확인 중...")
    
    results = {}
    
    # 파일 존재 확인
    files_to_check = [
        'topic_analyses.json',
        'topic_detailed_statistics.csv'
    ]
    
    for file_name in files_to_check:
        file_path = Path(output_dir) / 'csv' / file_name
        results[file_name] = file_path.exists()
        
        if file_path.exists():
            try:
                if file_name.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    results[f"{file_name}_topics"] = len(data)
                else:
                    df = pd.read_csv(file_path)
                    results[f"{file_name}_rows"] = len(df)
            except Exception as e:
                results[f"{file_name}_error"] = str(e)
    
    # 워드클라우드 확인
    wordcloud_dir = Path(output_dir) / 'wordclouds'
    if wordcloud_dir.exists():
        wordcloud_files = list(wordcloud_dir.glob('*.png'))
        results['wordcloud_files'] = len(wordcloud_files)
        results['wordcloud_names'] = [f.name for f in wordcloud_files]
    
    print(f"주제별 분석 결과 확인 완료: {results.get('topic_analyses.json_topics', 0)}개 주제")
    return results

def check_all_results(output_dir: str) -> Dict[str, Any]:
    """모든 분석 결과를 종합적으로 확인합니다."""
    print("=" * 60)
    print("전체 분석 결과 종합 확인")
    print("=" * 60)
    
    all_results = {
        'data_integrity': check_data_integrity('data_sample.xlsx'),
        'topic_discovery': check_topic_results(output_dir),
        'clustering': check_clustering_results(output_dir),
        'llm_analysis': check_llm_analysis_results(output_dir),
        'topic_analysis': check_topic_analysis_results(output_dir)
    }
    
    # 전체 요약
    summary = {
        'total_files_checked': sum([
            len([k for k in v.keys() if k.endswith('.csv') or k.endswith('.json')])
            for v in all_results.values()
        ]),
        'data_valid': all_results['data_integrity'].get('data_valid', False),
        'topics_found': all_results['topic_discovery'].get('total_topics', 0),
        'clusters_found': all_results['clustering'].get('total_clusters', 0),
        'llm_analysis_complete': all_results['llm_analysis'].get('analysis_results.json', False),
        'topic_analysis_complete': all_results['topic_analysis'].get('topic_analyses.json', False)
    }
    
    all_results['summary'] = summary
    
    print("\n📊 전체 결과 요약:")
    print(f"  데이터 유효성: {'✅' if summary['data_valid'] else '❌'}")
    print(f"  주제 발견: {summary['topics_found']}개 주제")
    print(f"  클러스터링: {summary['clusters_found']}개 클러스터")
    print(f"  LLM 분석: {'✅' if summary['llm_analysis_complete'] else '❌'}")
    print(f"  주제별 분석: {'✅' if summary['topic_analysis_complete'] else '❌'}")
    
    return all_results

def print_enhanced_topic_results(output_dir: str):
    """향상된 주제 발견 결과를 출력합니다."""
    print("=" * 60)
    print("🎯 LDA 주제 발견 결과 (최적 주제 수 자동 탐색)")
    print("=" * 60)
    
    try:
        # 주제별 상위 키워드 로드
        df = pd.read_csv(f'{output_dir}/csv/global_topics_top_terms.csv')
        assignments_df = pd.read_csv(f'{output_dir}/csv/topic_assignments.csv')
        
        # 주제별 정보 출력
        for topic_id in df['topic_id'].unique():
            topic_df = df[df['topic_id'] == topic_id]
            topic_name = topic_df['topic_name'].iloc[0]
            
            # 해당 주제에 할당된 문서들
            topic_assignments = assignments_df[assignments_df['topic_id'] == topic_id]
            
            print(f"\n📌 {topic_name}")
            print(f"   📊 포함된 내용 개수: {len(topic_assignments)}개")
            print(f"   🔑 주요 키워드: {', '.join(topic_df['term'].head(5).tolist())}")
            
            # 주제에 포함된 내용들
            print(f"   📝 포함된 내용:")
            for idx, row in topic_assignments.iterrows():
                print(f"      {row['document_id']+1}. {row['text']}")
            
            print("-" * 50)
        
        # 전체 통계
        print(f"\n📈 전체 통계:")
        print(f"   총 문서 수: {len(assignments_df)}개")
        print(f"   발견된 주제 수: {len(df['topic_id'].unique())}개")
        
        # 주제별 문서 수 분포
        topic_counts = assignments_df['topic_name'].value_counts()
        print(f"   주제별 분포:")
        for topic_name, count in topic_counts.items():
            print(f"      {topic_name}: {count}개")
            
    except FileNotFoundError as e:
        print(f"결과 파일을 찾을 수 없습니다: {e}")
        print("먼저 run_02_topic_discovery.py를 실행해주세요.")

if __name__ == "__main__":
    # 전체 결과 확인
    results = check_all_results("outputs")
    
    # 향상된 주제 결과 출력
    print_enhanced_topic_results("outputs") 