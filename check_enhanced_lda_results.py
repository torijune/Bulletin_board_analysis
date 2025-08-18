import pandas as pd
import json

def print_enhanced_topic_results():
    """향상된 주제 발견 결과를 출력합니다."""
    
    # 주제별 상위 키워드 로드
    try:
        df = pd.read_csv('outputs/csv/global_topics_top_terms.csv')
        assignments_df = pd.read_csv('outputs/csv/topic_assignments.csv')
        
        print("=" * 60)
        print("🎯 LDA 주제 발견 결과 (최적 주제 수 자동 탐색)")
        print("=" * 60)
        
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
    print_enhanced_topic_results() 