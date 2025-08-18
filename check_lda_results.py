import pandas as pd

# LDA 결과 로드
df = pd.read_csv('outputs/csv/global_topics_top_terms.csv')
print('LDA로 발견된 주제별 상위 단어:')

for topic_id in df['topic_id'].unique():
    topic_df = df[df['topic_id'] == topic_id]
    print(f'\n주제 {topic_id+1}:')
    print(topic_df[['term', 'score']].head(5).to_string(index=False))

print('\n' + '='*50)
print('문서별 주제 할당 결과:')
assignments_df = pd.read_csv('outputs/csv/topic_assignments.csv')
print(assignments_df[['document_id', 'topic_name', 'confidence', 'text']].to_string(index=False)) 