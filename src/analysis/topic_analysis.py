import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import json
import time
from typing import Dict, Any, List, Tuple
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
from src.utils.plotting import setup_korean_font, get_korean_font_prop

class TopicAnalysis:
    """주제별 상세 분석 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_client = None
        
        # .env 파일 로드
        load_dotenv()
        
        # LLM 클라이언트 초기화
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.llm_client = OpenAI(api_key=api_key)
                print("OpenAI 클라이언트 초기화 완료")
            else:
                print("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        except Exception as e:
            print(f"OpenAI 클라이언트 초기화 실패: {e}")
    
    def load_topic_data(self, csv_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """주제 관련 데이터를 로드합니다."""
        print("주제 데이터 로드 중...")
        
        # 주제별 문서 할당 데이터
        topic_assignments = pd.read_csv(f"{csv_dir}/topic_assignments.csv")
        
        # 주제별 키워드 데이터
        topic_keywords = pd.read_csv(f"{csv_dir}/global_topics_top_terms.csv")
        
        # 전처리된 원본 데이터
        preprocessed_data = pd.read_csv(f"{csv_dir}/preprocessed_data.csv")
        
        print(f"데이터 로드 완료:")
        print(f"  - 주제 할당: {len(topic_assignments)}개 문서")
        print(f"  - 주제 키워드: {len(topic_keywords)}개 키워드")
        print(f"  - 원본 데이터: {len(preprocessed_data)}개 문서")
        
        return topic_assignments, topic_keywords, preprocessed_data
    
    def extract_topic_texts(self, topic_assignments: pd.DataFrame, 
                          preprocessed_data: pd.DataFrame, 
                          topic_id: int) -> List[str]:
        """특정 주제에 할당된 문서들의 텍스트를 추출합니다."""
        # 해당 주제에 할당된 문서 인덱스 찾기
        topic_docs = topic_assignments[topic_assignments['topic_id'] == topic_id]
        doc_indices = topic_docs['document_id'].tolist()
        
        # 원본 데이터에서 해당 문서들의 텍스트 추출
        topic_texts = []
        for idx in doc_indices:
            if idx < len(preprocessed_data):
                text = preprocessed_data.iloc[idx]['cleaned_text']
                topic_texts.append(text)
        
        return topic_texts
    
    def create_topic_wordcloud(self, texts: List[str], topic_name: str, 
                             output_dir: str, topic_id: int) -> str:
        """주제별 워드클라우드를 생성합니다."""
        print(f"주제 {topic_id} 워드클라우드 생성 중...")
        
        # 텍스트 결합
        combined_text = ' '.join(texts)
        
        # 단어 빈도 계산
        words = combined_text.split()
        word_freq = Counter(words)
        
        # 한글 폰트 설정
        setup_korean_font()
        font_prop = get_korean_font_prop()
        
        # 워드클라우드 생성
        wordcloud = WordCloud(
            font_path=font_prop.get_file(),
            width=800,
            height=600,
            background_color='white',
            max_words=100,
            colormap='viridis',
            prefer_horizontal=0.7
        ).generate_from_frequencies(word_freq)
        
        # 워드클라우드 저장
        plt.figure(figsize=(12, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'주제 {topic_id}: {topic_name} 워드클라우드', 
                 fontproperties=font_prop, fontsize=16, pad=20)
        
        filename = f"{output_dir}/wordclouds/topic_{topic_id}_wordcloud.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"워드클라우드 저장 완료: {filename}")
        return filename
    
    def analyze_topic_with_llm(self, texts: List[str], topic_name: str, 
                             topic_keywords: List[str]) -> Dict[str, Any]:
        """LLM을 사용하여 주제를 상세 분석합니다."""
        if self.llm_client is None:
            print("LLM 클라이언트가 없어서 기본 분석을 수행합니다.")
            return self._basic_topic_analysis(texts, topic_name, topic_keywords)
        
        print(f"주제 '{topic_name}' LLM 분석 중...")
        
        # 분석용 텍스트 준비 (너무 길면 잘라내기)
        analysis_texts = texts[:10]  # 상위 10개 문서만 사용
        sample_texts = '\n'.join([f"- {text[:200]}..." for text in analysis_texts[:5]])
        
        # LLM 프롬프트 생성
        prompt = f"""
다음 상담 데이터를 분석하여 상세한 분석 결과를 제공해주세요.

주제명: {topic_name}
주요 키워드: {', '.join(topic_keywords[:10])}

주제에 포함된 상담 내용 예시:
{sample_texts}

다음 형식으로 JSON 형태로 분석 결과를 제공해주세요:

{{
    "주제_요약": "이 주제의 핵심 내용을 2-3문장으로 요약",
    "주요_문제점": ["문제점1", "문제점2", "문제점3"],
    "관련_행위자": ["행위자1", "행위자2", "행위자3"],
    "해결_방안": ["방안1", "방안2", "방안3"],
    "정책_시사점": "정책적 관점에서의 시사점",
    "우선순위": "높음/중간/낮음",
    "예상_빈도": "상담에서 차지하는 비중 예상"
}}

JSON 형식으로만 응답해주세요.
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 상담 데이터를 분석하는 전문가입니다. JSON 형식으로만 응답해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # JSON 파싱
            analysis_text = response.choices[0].message.content.strip()
            analysis_result = json.loads(analysis_text)
            
            # 추가 정보 추가
            analysis_result['분석_문서_수'] = len(texts)
            analysis_result['주제명'] = topic_name
            analysis_result['주요_키워드'] = topic_keywords[:10]
            
            print(f"LLM 분석 완료: {topic_name}")
            return analysis_result
            
        except Exception as e:
            print(f"LLM 분석 실패: {e}")
            return self._basic_topic_analysis(texts, topic_name, topic_keywords)
    
    def _basic_topic_analysis(self, texts: List[str], topic_name: str, 
                            topic_keywords: List[str]) -> Dict[str, Any]:
        """기본 주제 분석 (LLM 없이)"""
        print(f"주제 '{topic_name}' 기본 분석 중...")
        
        # 텍스트 통계
        text_lengths = [len(text) for text in texts]
        avg_length = np.mean(text_lengths)
        
        # 단어 빈도 분석
        combined_text = ' '.join(texts)
        words = combined_text.split()
        word_freq = Counter(words)
        top_words = word_freq.most_common(10)
        
        return {
            '주제명': topic_name,
            '분석_문서_수': len(texts),
            '주요_키워드': topic_keywords[:10],
            '평균_텍스트_길이': round(avg_length, 1),
            '상위_단어': [word for word, freq in top_words],
            '주제_요약': f"{topic_name} 관련 상담이 {len(texts)}건 있으며, 평균 {round(avg_length, 1)}자 길이의 텍스트로 구성됨",
            '주요_문제점': ["기본 분석으로는 구체적 문제점 파악 어려움"],
            '관련_행위자': ["상담인", "관리소장", "점유자"],
            '해결_방안': ["LLM 분석 필요"],
            '정책_시사점': "상세한 LLM 분석을 통해 정책적 시사점 도출 필요",
            '우선순위': "중간",
            '예상_빈도': f"전체의 약 {len(texts)}건"
        }
    
    def create_topic_statistics(self, topic_assignments: pd.DataFrame, 
                              topic_keywords: pd.DataFrame) -> pd.DataFrame:
        """주제별 통계를 생성합니다."""
        print("주제별 통계 생성 중...")
        
        topic_stats = []
        
        for topic_id in topic_assignments['topic_id'].unique():
            # 해당 주제의 문서 수
            topic_docs = topic_assignments[topic_assignments['topic_id'] == topic_id]
            doc_count = len(topic_docs)
            
            # 해당 주제의 키워드
            topic_kw = topic_keywords[topic_keywords['topic_id'] == topic_id]
            top_keywords = topic_kw.nlargest(5, 'score')['term'].tolist()
            
            # 평균 신뢰도
            avg_confidence = topic_docs['confidence'].mean()
            
            topic_stats.append({
                'topic_id': topic_id,
                'topic_name': topic_docs['topic_name'].iloc[0],
                'document_count': doc_count,
                'avg_confidence': round(avg_confidence, 3),
                'top_keywords': ', '.join(top_keywords),
                'percentage': round(doc_count / len(topic_assignments) * 100, 1)
            })
        
        stats_df = pd.DataFrame(topic_stats)
        return stats_df
    
    def generate_topic_report(self, topic_analyses: Dict[int, Dict[str, Any]], 
                            topic_stats: pd.DataFrame, output_dir: str):
        """주제별 분석 리포트를 생성합니다."""
        print("주제별 분석 리포트 생성 중...")
        
        # 마크다운 리포트 생성
        report_content = []
        report_content.append("# 주제별 상세 분석 리포트\n")
        report_content.append(f"생성일시: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 전체 요약
        total_docs = topic_stats['document_count'].sum()
        report_content.append("## 📊 전체 요약\n")
        report_content.append(f"- **총 문서 수**: {total_docs:,}개\n")
        report_content.append(f"- **발견된 주제 수**: {len(topic_stats)}개\n")
        report_content.append(f"- **평균 주제당 문서 수**: {total_docs/len(topic_stats):.1f}개\n\n")
        
        # 주제별 상세 분석
        for _, topic_stat in topic_stats.iterrows():
            topic_id = topic_stat['topic_id']
            topic_name = topic_stat['topic_name']
            
            if topic_id in topic_analyses:
                analysis = topic_analyses[topic_id]
                
                report_content.append(f"## 🎯 주제 {topic_id}: {topic_name}\n")
                report_content.append(f"**문서 수**: {topic_stat['document_count']}개 ({topic_stat['percentage']}%)\n")
                report_content.append(f"**평균 신뢰도**: {topic_stat['avg_confidence']}\n\n")
                
                # LLM 분석 결과
                report_content.append("### 📋 상세 분석\n")
                report_content.append(f"**주제 요약**: {analysis.get('주제_요약', 'N/A')}\n\n")
                
                # 주요 문제점
                problems = analysis.get('주요_문제점', [])
                if problems:
                    report_content.append("**주요 문제점**:\n")
                    for problem in problems:
                        report_content.append(f"- {problem}\n")
                    report_content.append("\n")
                
                # 관련 행위자
                actors = analysis.get('관련_행위자', [])
                if actors:
                    report_content.append("**관련 행위자**:\n")
                    for actor in actors:
                        report_content.append(f"- {actor}\n")
                    report_content.append("\n")
                
                # 해결 방안
                solutions = analysis.get('해결_방안', [])
                if solutions:
                    report_content.append("**해결 방안**:\n")
                    for solution in solutions:
                        report_content.append(f"- {solution}\n")
                    report_content.append("\n")
                
                # 정책 시사점
                policy = analysis.get('정책_시사점', 'N/A')
                report_content.append(f"**정책 시사점**: {policy}\n\n")
                
                # 우선순위 및 빈도
                priority = analysis.get('우선순위', 'N/A')
                frequency = analysis.get('예상_빈도', 'N/A')
                report_content.append(f"**우선순위**: {priority}\n")
                report_content.append(f"**예상 빈도**: {frequency}\n\n")
                
                # 워드클라우드 이미지 참조
                report_content.append(f"![워드클라우드](wordclouds/topic_{topic_id}_wordcloud.png)\n\n")
                
                report_content.append("---\n\n")
        
        # 리포트 저장
        report_path = f"{output_dir}/reports/topic_analysis_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(''.join(report_content))
        
        print(f"주제별 분석 리포트 저장 완료: {report_path}")
        return report_path
    
    def analyze_all_topics(self, csv_dir: str, output_dir: str) -> Dict[str, Any]:
        """모든 주제에 대해 상세 분석을 수행합니다."""
        print("=" * 60)
        print("주제별 상세 분석 시작")
        print("=" * 60)
        
        # 데이터 로드
        topic_assignments, topic_keywords, preprocessed_data = self.load_topic_data(csv_dir)
        
        # 주제별 통계 생성
        topic_stats = self.create_topic_statistics(topic_assignments, topic_keywords)
        topic_stats.to_csv(f"{output_dir}/csv/topic_detailed_statistics.csv", 
                          index=False, encoding='utf-8-sig')
        
        # 주제별 상세 분석
        topic_analyses = {}
        
        for topic_id in topic_assignments['topic_id'].unique():
            print(f"\n{'='*20} 주제 {topic_id} 분석 {'='*20}")
            
            # 해당 주제의 텍스트 추출
            topic_texts = self.extract_topic_texts(topic_assignments, preprocessed_data, topic_id)
            
            if not topic_texts:
                print(f"주제 {topic_id}에 할당된 문서가 없습니다.")
                continue
            
            # 주제명과 키워드 가져오기
            topic_docs = topic_assignments[topic_assignments['topic_id'] == topic_id]
            topic_name = topic_docs['topic_name'].iloc[0]
            
            topic_kw = topic_keywords[topic_keywords['topic_id'] == topic_id]
            topic_keywords_list = topic_kw.nlargest(10, 'score')['term'].tolist()
            
            # 워드클라우드 생성
            self.create_topic_wordcloud(topic_texts, topic_name, output_dir, topic_id)
            
            # LLM 분석
            analysis_result = self.analyze_topic_with_llm(topic_texts, topic_name, topic_keywords_list)
            topic_analyses[topic_id] = analysis_result
            
            # API 호출 제한을 위한 대기
            time.sleep(0.5)
        
        # 분석 결과 저장 (키를 문자열로 변환)
        topic_analyses_str_keys = {str(k): v for k, v in topic_analyses.items()}
        with open(f"{output_dir}/csv/topic_analyses.json", 'w', encoding='utf-8') as f:
            json.dump(topic_analyses_str_keys, f, ensure_ascii=False, indent=2)
        
        # 리포트 생성
        self.generate_topic_report(topic_analyses, topic_stats, output_dir)
        
        print("\n" + "=" * 60)
        print("주제별 상세 분석 완료")
        print("=" * 60)
        
        return {
            'topic_analyses': topic_analyses,
            'topic_stats': topic_stats,
            'total_topics': len(topic_analyses)
        } 