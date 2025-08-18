import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
import json
from src.utils.text_processing import clean_text_for_wordcloud
from src.utils.plotting import setup_korean_font, get_korean_font_prop

class ReportGenerator:
    """분석 리포트 생성 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_config = config['output']
        
    def generate_wordcloud(self, texts: List[str], title: str, output_path: str):
        """워드클라우드를 생성합니다."""
        # 텍스트 전처리 및 결합
        cleaned_texts = []
        for text in texts:
            cleaned_text = clean_text_for_wordcloud(text)
            if cleaned_text:
                cleaned_texts.append(cleaned_text)
        
        if not cleaned_texts:
            print(f"워드클라우드 생성 실패: 유효한 텍스트가 없습니다. {output_path}")
            return
        
        combined_text = ' '.join(cleaned_texts)
        
        # 한글 폰트 설정
        try:
            wordcloud = WordCloud(
                font_path='/System/Library/Fonts/AppleGothic.ttf',  # macOS
                width=800,
                height=400,
                background_color='white',
                max_words=50,  # 더 적은 단어로 깔끔하게
                colormap='viridis',
                min_font_size=10,
                max_font_size=100,
                relative_scaling=0.5,
                random_state=42
            ).generate(combined_text)
        except:
            # 폰트를 찾을 수 없는 경우 기본 설정
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=50,
                colormap='viridis',
                min_font_size=10,
                max_font_size=100,
                relative_scaling=0.5,
                random_state=42
            ).generate(combined_text)
        
        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"워드클라우드 저장 완료: {output_path}")
    
    def generate_frequency_chart(self, data: pd.DataFrame, x_col: str, y_col: str, 
                               title: str, output_path: str):
        """빈도 차트를 생성합니다."""
        # 한글 폰트 설정
        setup_korean_font()
        font_prop = get_korean_font_prop()
        
        plt.figure(figsize=(12, 6))
        sns.barplot(data=data, x=x_col, y=y_col)
        plt.title(title, fontproperties=font_prop, fontsize=16)
        plt.xlabel('클러스터', fontproperties=font_prop, fontsize=12)
        plt.ylabel('문서 수', fontproperties=font_prop, fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"빈도 차트 저장 완료: {output_path}")
    
    def generate_markdown_report(self, topic_results: Dict[str, Any], 
                               cluster_results: Dict[str, Any],
                               analysis_results: List[Dict[str, Any]],
                               output_dir: str):
        """마크다운 리포트를 생성합니다."""
        report_content = self._create_report_content(
            topic_results, cluster_results, analysis_results
        )
        
        report_path = Path(output_dir) / "분석_리포트.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"마크다운 리포트 저장 완료: {report_path}")
    
    def _create_report_content(self, topic_results: Dict[str, Any],
                             cluster_results: Dict[str, Any],
                             analysis_results: List[Dict[str, Any]]) -> str:
        """리포트 내용을 생성합니다."""
        content = f"""# 상담/게시판 데이터 주제 발견 및 심층 분석 리포트

## 📊 분석 개요

이 리포트는 상담/게시판 데이터를 대상으로 자동화된 주제 발견 및 심층 분석을 수행한 결과입니다.

### 분석 방법론
- **주제 발견**: LDA (Latent Dirichlet Allocation) 알고리즘 사용
- **클러스터링**: K-means 클러스터링 + Sentence-BERT 임베딩
- **심층 분석**: LLM 기반 텍스트 분석

## 🎯 주제 발견 결과

### 전체 주제 분포
총 {len(topic_results.get('top_terms', {}))}개의 주요 주제가 발견되었습니다.

"""
        
        # 주제별 상세 정보
        if 'top_terms' in topic_results:
            content += "### 주제별 상위 키워드\n\n"
            for topic_id, terms in topic_results['top_terms'].items():
                content += f"#### 주제 {topic_id + 1}\n"
                content += "**상위 키워드:** "
                content += ", ".join([term for term, _ in terms[:5]])
                content += "\n\n"
        
        # 클러스터링 결과
        if cluster_results:
            content += "## 🔍 클러스터링 결과\n\n"
            content += f"총 {len(cluster_results.get('cluster_stats', []))}개의 클러스터가 생성되었습니다.\n\n"
            
            for _, cluster in cluster_results.get('cluster_stats', []).iterrows():
                content += f"### {cluster['cluster_name']}\n"
                content += f"- **문서 수**: {cluster['document_count']}개\n"
                content += f"- **평균 유사도**: {cluster['avg_similarity']:.3f}\n"
                content += f"- **대표 문서**: {cluster['representative_text'][:100]}...\n\n"
        
        # LLM 분석 결과
        if analysis_results:
            content += "## 🤖 LLM 심층 분석 결과\n\n"
            
            for result in analysis_results:
                cluster_name = result['cluster_name']
                topic_name = result['topic_name']
                summary = result['cluster_summary']
                
                content += f"### {cluster_name} ({topic_name})\n\n"
                content += "#### 주요 분석 결과\n"
                content += f"- **주요 원인**: {summary.get('주요_원인', '분석 불가')}\n"
                content += f"- **주요 행위자**: {summary.get('주요_행위자', '분석 불가')}\n"
                content += f"- **공통 요구사항**: {summary.get('공통_요구사항', '분석 불가')}\n"
                content += f"- **전체 톤**: {summary.get('전체_톤', '분석 불가')}\n"
                content += f"- **주요 리스크**: {summary.get('주요_리스크', '분석 불가')}\n"
                content += f"- **해결 우선순위**: {summary.get('해결_우선순위', '분석 불가')}\n"
                content += f"- **정책 개선점**: {summary.get('정책_개선점', '분석 불가')}\n\n"
        
        # 정책 제언
        content += """## 💡 정책 제언

### 주요 발견사항
1. **주제별 분포**: 상담 데이터에서 특정 주제들이 집중적으로 나타남
2. **클러스터 특성**: 각 클러스터별로 고유한 문제 패턴 발견
3. **LLM 분석**: 정량적 분석을 통한 정책 개선 방향 제시

### 정책 개선 방안
- **즉시 대응**: 우선순위가 높은 문제들에 대한 즉시 대응 체계 구축
- **예방적 조치**: 반복 발생하는 문제에 대한 예방적 정책 수립
- **모니터링 강화**: 주제별 트렌드 모니터링 시스템 구축

## 📈 시각화 결과

분석 과정에서 생성된 시각화 결과는 다음과 같습니다:
- 주제 분포 차트
- 클러스터별 문서 수 분포
- 워드클라우드
- 빈도 분석 차트

## 🔧 기술적 세부사항

### 사용된 기술
- **주제 발견**: scikit-learn LDA
- **임베딩**: Sentence-BERT
- **클러스터링**: K-means
- **텍스트 분석**: OpenAI GPT 모델
- **시각화**: matplotlib, seaborn, wordcloud

### 데이터 처리
- 텍스트 전처리 및 정규화
- 개인정보 마스킹
- 중복 제거 및 품질 관리

---
*이 리포트는 자동화된 분석 시스템에 의해 생성되었습니다.*
"""
        
        return content
    
    def generate_all_visualizations(self, topic_results: Dict[str, Any],
                                   cluster_results: Dict[str, Any],
                                   texts: List[str],
                                   output_dir: str):
        """모든 시각화를 생성합니다."""
        output_path = Path(output_dir)
        
        # 주제별 워드클라우드
        if 'top_terms' in topic_results:
            # 주제 할당 결과 로드
            topic_assignments_path = Path(output_dir) / "csv" / "topic_assignments.csv"
            if topic_assignments_path.exists():
                topic_assignments = pd.read_csv(topic_assignments_path)
                
                for topic_id, terms in topic_results['top_terms'].items():
                    # 해당 주제에 할당된 문서들만 필터링
                    topic_mask = topic_assignments['topic_id'] == topic_id
                    topic_doc_ids = topic_assignments[topic_mask]['document_id'].tolist()
                    topic_texts = [texts[doc_id] for doc_id in topic_doc_ids if doc_id < len(texts)]
                    
                    if topic_texts:  # 텍스트가 있는 경우에만 워드클라우드 생성
                        wordcloud_path = output_path / "visualizations" / "wordclouds" / f"topic_{topic_id+1}_wordcloud.png"
                        self.generate_wordcloud(
                            topic_texts,
                            f"Topic {topic_id+1} Word Cloud",
                            str(wordcloud_path)
                        )
                    else:
                        print(f"주제 {topic_id+1}에 할당된 문서가 없어서 워드클라우드를 생성하지 않습니다.")
            else:
                print("주제 할당 파일을 찾을 수 없어서 전체 텍스트로 워드클라우드를 생성합니다.")
                for topic_id, terms in topic_results['top_terms'].items():
                    wordcloud_path = output_path / "visualizations" / "wordclouds" / f"topic_{topic_id+1}_wordcloud.png"
                    self.generate_wordcloud(
                        texts,
                        f"Topic {topic_id+1} Word Cloud",
                        str(wordcloud_path)
                    )
                
                wordcloud_path = output_path / "visualizations" / "wordclouds" / f"topic_{topic_id+1}_wordcloud.png"
                self.generate_wordcloud(
                    topic_texts,
                    f"Topic {topic_id+1} Word Cloud",
                    str(wordcloud_path)
                )
        
        # 클러스터별 워드클라우드
        if 'cluster_stats' in cluster_results:
            for _, cluster in cluster_results['cluster_stats'].iterrows():
                cluster_texts = cluster['sample_texts']
                
                wordcloud_path = output_path / "visualizations" / "wordclouds" / f"{cluster['cluster_name']}_wordcloud.png"
                self.generate_wordcloud(
                    cluster_texts,
                    f"{cluster['cluster_name']} Word Cloud",
                    str(wordcloud_path)
                )
        
        # 빈도 차트
        if 'cluster_stats' in cluster_results:
            freq_path = output_path / "visualizations" / "frequency_charts" / "cluster_frequency.png"
            self.generate_frequency_chart(
                cluster_results['cluster_stats'],
                'cluster_name',
                'document_count',
                'Cluster Distribution by Document Count',
                str(freq_path)
            )
        
        print("모든 시각화 생성 완료") 