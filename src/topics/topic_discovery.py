import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Tuple
import json
from gensim.models import CoherenceModel
from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel
import openai
from openai import OpenAI
import time
import os
from dotenv import load_dotenv
from src.utils.plotting import setup_korean_font, get_korean_font_prop

class TopicDiscovery:
    """주제 발견 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.topic_config = config['topic_discovery']
        self.vectorizer = None
        self.model = None
        self.feature_names = None
        self.llm_client = None
        
        # .env 파일 로드
        load_dotenv()
        
        # LLM 클라이언트 초기화
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.llm_client = OpenAI(api_key=api_key)
                print("OpenAI 클라이언트 초기화 완료 (.env 파일에서 API 키 로드)")
            else:
                print("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        except Exception as e:
            print(f"OpenAI 클라이언트 초기화 실패: {e}")
            print("API 키를 .env 파일의 OPENAI_API_KEY에 설정해주세요.")
    
    def find_optimal_topics(self, texts: List[str], max_topics: int = 15) -> int:
        """최적의 주제 수를 찾습니다."""
        print("최적 주제 수 탐색 중...")
        
        # 대용량 데이터 처리 설정 확인
        large_scale_config = self.topic_config.get('large_scale', {})
        if large_scale_config.get('enabled', False):
            max_topics = min(max_topics, large_scale_config.get('max_topics_search', 10))
            print(f"대용량 데이터 모드: 최대 주제 수 탐색 범위를 {max_topics}로 제한")
        
        # 텍스트 전처리
        processed_texts = []
        for text in texts:
            # 간단한 토큰화 (실제로는 더 정교한 전처리 필요)
            tokens = text.split()
            processed_texts.append(tokens)
        
        # Dictionary 생성
        dictionary = Dictionary(processed_texts)
        dictionary.filter_extremes(no_below=2, no_above=0.5)
        
        # 코퍼스 생성
        corpus = [dictionary.doc2bow(text) for text in processed_texts]
        
        # Coherence Score 계산
        coherence_scores = []
        topic_range = range(2, min(max_topics + 1, len(texts) // 2))
        
        for n_topics in topic_range:
            try:
                # LDA 모델 학습
                lda_model = LdaModel(
                    corpus=corpus,
                    id2word=dictionary,
                    num_topics=n_topics,
                    random_state=42,
                    passes=10,
                    alpha='auto',
                    per_word_topics=True
                )
                
                # Coherence Score 계산
                coherence_model = CoherenceModel(
                    model=lda_model,
                    texts=processed_texts,
                    dictionary=dictionary,
                    coherence='c_v'
                )
                
                coherence_score = coherence_model.get_coherence()
                coherence_scores.append(coherence_score)
                
                print(f"  주제 수 {n_topics}: Coherence Score = {coherence_score:.4f}")
                
            except Exception as e:
                print(f"  주제 수 {n_topics}에서 오류 발생: {e}")
                coherence_scores.append(0)
        
        # 최적 주제 수 선택
        optimal_topics = topic_range[np.argmax(coherence_scores)]
        print(f"최적 주제 수: {optimal_topics} (Coherence Score: {max(coherence_scores):.4f})")
        
        return optimal_topics
    
    def fit(self, texts: List[str]) -> 'TopicDiscovery':
        """주제 모델을 학습합니다."""
        print("주제 발견 모델 학습 시작...")
        
        # 대용량 데이터 처리 설정 확인
        large_scale_config = self.topic_config.get('large_scale', {})
        if large_scale_config.get('enabled', False):
            texts = self._handle_large_scale_data(texts, large_scale_config)
        
        # 최적 주제 수 찾기
        if self.topic_config.get('auto_find_topics', True):
            optimal_topics = self.find_optimal_topics(texts)
            self.topic_config['n_topics'] = optimal_topics
        
        # 벡터라이저 설정
        self.vectorizer = CountVectorizer(
            min_df=self.topic_config['min_df'],
            max_df=self.topic_config['max_df'],
            stop_words=None,  # 한글은 별도 처리 필요
            ngram_range=(1, 2)
        )
        
        # 텍스트 벡터화
        X = self.vectorizer.fit_transform(texts)
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        # 주제 모델 학습
        algorithm = self.topic_config['algorithm'].lower()
        
        if algorithm == 'lda':
            self.model = LatentDirichletAllocation(
                n_components=self.topic_config['n_topics'],
                random_state=42,
                max_iter=100
            )
        elif algorithm == 'nmf':
            self.model = NMF(
                n_components=self.topic_config['n_topics'],
                random_state=42,
                max_iter=100
            )
        else:
            raise ValueError(f"지원하지 않는 알고리즘: {algorithm}")
        
        self.model.fit(X)
        print(f"주제 발견 모델 학습 완료: {self.topic_config['n_topics']}개 주제")
        
        return self
    
    def _handle_large_scale_data(self, texts: List[str], config: Dict[str, Any]) -> List[str]:
        """대용량 데이터를 효율적으로 처리합니다."""
        print(f"대용량 데이터 처리 모드 활성화 (원본 데이터: {len(texts)}개)")
        
        # 샘플링 크기 확인
        sample_size = config.get('sample_size', 1000)
        
        if len(texts) > sample_size:
            # 랜덤 샘플링
            import random
            random.seed(42)
            sampled_indices = random.sample(range(len(texts)), sample_size)
            sampled_texts = [texts[i] for i in sampled_indices]
            
            print(f"데이터 샘플링: {len(texts)}개 → {len(sampled_texts)}개")
            return sampled_texts
        else:
            print(f"데이터 크기가 샘플링 기준({sample_size}개) 이하이므로 전체 데이터 사용")
            return texts
    
    def generate_topic_names(self, texts: List[str]) -> Dict[int, str]:
        """LLM을 사용하여 주제명을 생성합니다."""
        # 대용량 데이터 처리 설정 확인
        large_scale_config = self.topic_config.get('large_scale', {})
        if large_scale_config.get('use_keyword_naming', False):
            print("대용량 데이터 모드: 키워드 기반 주제명 생성 사용")
            return self._generate_topic_names_from_keywords(texts)
        
        if self.llm_client is None:
            print("LLM 클라이언트가 없어서 키워드 기반 주제명을 생성합니다.")
            return self._generate_topic_names_from_keywords(texts)
        
        topic_assignments, _ = self.assign_topics(texts)
        topic_names = {}
        
        for topic_id in range(self.topic_config['n_topics']):
            # 해당 주제에 할당된 문서들 수집
            topic_texts = [texts[i] for i in range(len(texts)) if topic_assignments[i] == topic_id]
            
            if not topic_texts:
                topic_names[topic_id] = f"주제_{topic_id+1}"
                continue
            
            # 주제별 상위 키워드 가져오기
            top_terms = self.get_top_terms()
            topic_keywords = [term for term, _ in top_terms[topic_id][:10]]
            
            # 대용량 데이터에서는 대표 문서 수를 제한
            max_example_texts = 3 if len(topic_texts) <= 10 else 1
            example_texts = topic_texts[:max_example_texts]
            
            # LLM 프롬프트 생성
            prompt = f"""
다음 상담 데이터를 분석하여 적절한 주제명을 생성해주세요.

주제 키워드: {', '.join(topic_keywords)}

주제에 포함된 상담 내용 예시:
{chr(10).join([f"- {text[:100]}..." for text in example_texts])}

위 내용을 종합하여 3-5단어로 된 간결하고 명확한 주제명을 생성해주세요.
주제명만 응답해주세요.
"""
            
            try:
                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 상담 데이터를 분석하여 주제명을 생성하는 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=50,
                    temperature=0.1
                )
                
                topic_name = response.choices[0].message.content.strip()
                topic_names[topic_id] = topic_name
                
                print(f"주제 {topic_id+1} 이름 생성: {topic_name}")
                
                # API 호출 제한을 위한 대기
                time.sleep(0.1)
                
            except Exception as e:
                print(f"주제 {topic_id+1} 이름 생성 실패: {e}")
                topic_names[topic_id] = f"주제_{topic_id+1}"
        
        return topic_names
    
    def _generate_topic_names_from_keywords(self, texts: List[str]) -> Dict[int, str]:
        """키워드 기반으로 주제명을 생성합니다."""
        topic_assignments, _ = self.assign_topics(texts)
        topic_names = {}
        
        for topic_id in range(self.topic_config['n_topics']):
            # 주제별 상위 키워드 가져오기
            top_terms = self.get_top_terms()
            topic_keywords = [term for term, _ in top_terms[topic_id][:5]]
            
            # 키워드 기반 주제명 생성
            if '관리비' in topic_keywords or '관리규약' in topic_keywords:
                topic_names[topic_id] = "관리비/관리규약 관련"
            elif '선거' in topic_keywords or '무효' in topic_keywords:
                topic_names[topic_id] = "선거/분쟁 관련"
            elif '회계감사' in topic_keywords or '회계' in topic_keywords:
                topic_names[topic_id] = "회계/감사 관련"
            elif '건축물' in topic_keywords or '건축' in topic_keywords:
                topic_names[topic_id] = "건축/시설 관련"
            else:
                # 주요 키워드들을 조합
                main_keywords = [kw for kw in topic_keywords if len(kw) > 1][:3]
                topic_names[topic_id] = f"{'/'.join(main_keywords)} 관련"
            
            print(f"주제 {topic_id+1} 이름 생성: {topic_names[topic_id]}")
        
        return topic_names
        
        topic_assignments, _ = self.assign_topics(texts)
        topic_names = {}
        
        for topic_id in range(self.topic_config['n_topics']):
            # 해당 주제에 할당된 문서들 수집
            topic_texts = [texts[i] for i in range(len(texts)) if topic_assignments[i] == topic_id]
            
            if not topic_texts:
                topic_names[topic_id] = f"주제_{topic_id+1}"
                continue
            
            # 주제별 상위 키워드 가져오기
            top_terms = self.get_top_terms()
            topic_keywords = [term for term, _ in top_terms[topic_id][:10]]
            
            # LLM 프롬프트 생성
            prompt = f"""
다음 상담 데이터를 분석하여 적절한 주제명을 생성해주세요.

주제 키워드: {', '.join(topic_keywords)}

주제에 포함된 상담 내용 예시:
{chr(10).join([f"- {text[:100]}..." for text in topic_texts[:3]])}

위 내용을 종합하여 3-5단어로 된 간결하고 명확한 주제명을 생성해주세요.
주제명만 응답해주세요.
"""
            
            try:
                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 상담 데이터를 분석하여 주제명을 생성하는 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=50,
                    temperature=0.1
                )
                
                topic_name = response.choices[0].message.content.strip()
                topic_names[topic_id] = topic_name
                
                print(f"주제 {topic_id+1} 이름 생성: {topic_name}")
                
                # API 호출 제한을 위한 대기
                time.sleep(0.1)
                
            except Exception as e:
                print(f"주제 {topic_id+1} 이름 생성 실패: {e}")
                topic_names[topic_id] = f"주제_{topic_id+1}"
        
        return topic_names
    
    def get_top_terms(self, n_terms: int = None) -> Dict[int, List[Tuple[str, float]]]:
        """각 주제별 상위 단어를 반환합니다."""
        if n_terms is None:
            n_terms = self.topic_config['top_terms_per_topic']
        
        top_terms = {}
        
        for topic_idx, topic in enumerate(self.model.components_):
            top_indices = topic.argsort()[-n_terms:][::-1]
            top_terms[topic_idx] = [
                (self.feature_names[i], topic[i]) 
                for i in top_indices
            ]
        
        return top_terms
    
    def assign_topics(self, texts: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """각 문서에 주제를 할당합니다."""
        X = self.vectorizer.transform(texts)
        topic_distributions = self.model.transform(X)
        
        # 가장 관련성 높은 주제 할당
        topic_assignments = topic_distributions.argmax(axis=1)
        confidence_scores = topic_distributions.max(axis=1)
        
        return topic_assignments, confidence_scores
    
    def create_topic_summary(self, texts: List[str]) -> pd.DataFrame:
        """주제별 요약 정보를 생성합니다."""
        topic_assignments, confidence_scores = self.assign_topics(texts)
        top_terms = self.get_top_terms()
        
        # LLM으로 주제명 생성
        topic_names = self.generate_topic_names(texts)
        
        # 주제별 통계
        topic_stats = []
        for topic_id in range(self.topic_config['n_topics']):
            topic_mask = topic_assignments == topic_id
            topic_texts = [texts[i] for i in range(len(texts)) if topic_mask[i]]
            
            topic_stats.append({
                'topic_id': topic_id,
                'topic_name': topic_names[topic_id],
                'document_count': len(topic_texts),
                'avg_confidence': confidence_scores[topic_mask].mean() if len(topic_texts) > 0 else 0,
                'top_terms': [term for term, _ in top_terms[topic_id][:5]],
                'representative_texts': topic_texts[:3] if topic_texts else []
            })
        
        return pd.DataFrame(topic_stats)
    
    def save_results(self, texts: List[str], output_dir: str):
        """결과를 파일로 저장합니다."""
        # 주제별 상위 단어 저장
        top_terms = self.get_top_terms()
        topic_names = self.generate_topic_names(texts)
        top_terms_data = []
        
        for topic_id, terms in top_terms.items():
            for term, score in terms:
                top_terms_data.append({
                    'topic_id': topic_id,
                    'topic_name': topic_names[topic_id],
                    'term': term,
                    'score': score
                })
        
        top_terms_df = pd.DataFrame(top_terms_data)
        top_terms_df.to_csv(f"{output_dir}/global_topics_top_terms.csv", index=False, encoding='utf-8-sig')
        
        # 문서별 주제 할당 저장
        topic_assignments, confidence_scores = self.assign_topics(texts)
        assignments_data = []
        
        for i, (topic_id, confidence) in enumerate(zip(topic_assignments, confidence_scores)):
            assignments_data.append({
                'document_id': i,
                'topic_id': topic_id,
                'topic_name': topic_names[topic_id],
                'confidence': confidence,
                'text': texts[i][:100] + '...' if len(texts[i]) > 100 else texts[i]
            })
        
        assignments_df = pd.DataFrame(assignments_data)
        assignments_df.to_csv(f"{output_dir}/topic_assignments.csv", index=False, encoding='utf-8-sig')
        
        # 주제별 요약 저장
        topic_summary = self.create_topic_summary(texts)
        topic_summary.to_csv(f"{output_dir}/topic_summary.csv", index=False, encoding='utf-8-sig')
        
        # 주제별로 문서 분리하여 저장
        self.save_topic_documents(texts, topic_assignments, topic_names, output_dir)
        
        print(f"결과 저장 완료: {output_dir}")
    
    def save_topic_documents(self, texts: List[str], topic_assignments: np.ndarray, topic_names: Dict[int, str], output_dir: str):
        """주제별로 문서를 분리하여 저장합니다."""
        print("주제별 문서 분리 및 저장 중...")
        
        # 주제별로 문서 그룹화
        topic_documents = {}
        for i, (text, topic_id) in enumerate(zip(texts, topic_assignments)):
            if topic_id not in topic_documents:
                topic_documents[topic_id] = []
            topic_documents[topic_id].append({
                'document_id': i,
                'text': text,
                'topic_id': topic_id,
                'topic_name': topic_names[topic_id]
            })
        
        # 각 주제별로 CSV 파일 저장
        for topic_id, documents in topic_documents.items():
            topic_name = topic_names[topic_id]
            # 파일명에 사용할 수 있도록 특수문자 제거
            safe_topic_name = topic_name.replace('/', '_').replace(' ', '_').replace(':', '_')
            
            topic_df = pd.DataFrame(documents)
            filename = f"{output_dir}/topic_{topic_id}_{safe_topic_name}_documents.csv"
            topic_df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"  주제 {topic_id} ({topic_name}): {len(documents)}개 문서 -> {filename}")
        
        # 전체 주제별 문서 인덱스 저장
        all_topic_docs = []
        for topic_id, documents in topic_documents.items():
            for doc in documents:
                all_topic_docs.append(doc)
        
        all_topic_df = pd.DataFrame(all_topic_docs)
        all_topic_df.to_csv(f"{output_dir}/all_topic_documents.csv", index=False, encoding='utf-8-sig')
        print(f"  전체 주제별 문서 인덱스: {len(all_topic_docs)}개 문서 -> {output_dir}/all_topic_documents.csv")
    
    def visualize_topics(self, output_dir: str):
        """주제 분포를 시각화합니다."""
        # 주제별 문서 수 시각화
        topic_summary = pd.read_csv(f"{output_dir}/../csv/topic_summary.csv")
        
        # 한글 폰트 설정
        setup_korean_font()
        font_prop = get_korean_font_prop()
        
        plt.figure(figsize=(12, 6))
        sns.barplot(data=topic_summary, x='topic_name', y='document_count')
        plt.title('주제별 문서 수 분포', fontproperties=font_prop, fontsize=16)
        plt.xlabel('주제', fontproperties=font_prop, fontsize=12)
        plt.ylabel('문서 수', fontproperties=font_prop, fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/topic_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"시각화 저장 완료: {output_dir}/topic_distribution.png") 