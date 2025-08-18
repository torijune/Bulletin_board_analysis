import json
import pandas as pd
from typing import Dict, Any, List, Optional
import openai
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

class LLMAnalyzer:
    """LLM을 사용한 텍스트 분석 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_config = config['llm']
        self.client = None
        
        # .env 파일 로드
        load_dotenv()
        
        # OpenAI 클라이언트 초기화
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
                print("OpenAI 클라이언트 초기화 완료 (.env 파일에서 API 키 로드)")
            else:
                print("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        except Exception as e:
            print(f"OpenAI 클라이언트 초기화 실패: {e}")
            print("API 키를 .env 파일의 OPENAI_API_KEY에 설정해주세요.")
    
    def analyze_document(self, text: str, topic_name: str = "일반") -> Dict[str, Any]:
        """단일 문서를 분석합니다."""
        if self.client is None:
            return self._mock_analysis(text, topic_name)
        
        prompt = self._create_analysis_prompt(text, topic_name)
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_config['model'],
                messages=[
                    {"role": "system", "content": "당신은 상담 데이터를 분석하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.llm_config['max_tokens'],
                temperature=self.llm_config['temperature']
            )
            
            result_text = response.choices[0].message.content
            return self._parse_analysis_result(result_text)
            
        except Exception as e:
            print(f"LLM 분석 실패: {e}")
            return self._mock_analysis(text, topic_name)
    
    def _create_analysis_prompt(self, text: str, topic_name: str) -> str:
        """분석 프롬프트를 생성합니다."""
        return f"""
다음 상담 내용을 분석하여 JSON 형태로 결과를 제공해주세요.

상담 내용: {text}
주제: {topic_name}

다음 JSON 구조로 분석 결과를 제공해주세요:
{{
    "원인": "문제가 발생한 주요 원인",
    "행위자": "관련된 주요 행위자들",
    "요구사항": "상담인의 주요 요구사항",
    "톤": "상담 내용의 톤 (긍정적/부정적/중립적)",
    "리스크": "예상되는 리스크나 문제점",
    "해결방안": "제안할 수 있는 해결방안",
    "정책적_시사점": "정책 개선을 위한 시사점"
}}

JSON만 응답해주세요.
"""
    
    def _parse_analysis_result(self, result_text: str) -> Dict[str, Any]:
        """LLM 응답을 파싱합니다."""
        try:
            # JSON 부분만 추출
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("JSON 형식을 찾을 수 없습니다")
            
            json_str = result_text[start_idx:end_idx]
            return json.loads(json_str)
            
        except Exception as e:
            print(f"JSON 파싱 실패: {e}")
            return self._create_default_analysis()
    
    def _mock_analysis(self, text: str, topic_name: str) -> Dict[str, Any]:
        """LLM이 없을 때 사용하는 모의 분석"""
        return {
            "원인": "분석 불가",
            "행위자": "분석 불가",
            "요구사항": "분석 불가",
            "톤": "중립적",
            "리스크": "분석 불가",
            "해결방안": "분석 불가",
            "정책적_시사점": "분석 불가"
        }
    
    def _create_default_analysis(self) -> Dict[str, Any]:
        """기본 분석 결과"""
        return {
            "원인": "분석 실패",
            "행위자": "분석 실패",
            "요구사항": "분석 실패",
            "톤": "중립적",
            "리스크": "분석 실패",
            "해결방안": "분석 실패",
            "정책적_시사점": "분석 실패"
        }
    
    def analyze_cluster(self, texts: List[str], cluster_name: str, topic_name: str = "일반") -> Dict[str, Any]:
        """클러스터 전체를 분석합니다."""
        print(f"클러스터 분석 시작: {cluster_name}")
        
        # 각 문서 분석
        individual_analyses = []
        for i, text in enumerate(texts):
            print(f"문서 {i+1}/{len(texts)} 분석 중...")
            analysis = self.analyze_document(text, topic_name)
            analysis['document_index'] = i
            analysis['text'] = text[:100] + "..." if len(text) > 100 else text
            individual_analyses.append(analysis)
            
            # API 호출 제한을 위한 대기
            time.sleep(0.1)
        
        # 클러스터 전체 요약
        cluster_summary = self._summarize_cluster(individual_analyses, cluster_name, topic_name)
        
        return {
            'cluster_name': cluster_name,
            'topic_name': topic_name,
            'individual_analyses': individual_analyses,
            'cluster_summary': cluster_summary
        }
    
    def _summarize_cluster(self, analyses: List[Dict[str, Any]], cluster_name: str, topic_name: str) -> Dict[str, Any]:
        """클러스터 분석 결과를 요약합니다."""
        if self.client is None:
            return self._create_default_cluster_summary()
        
        # 분석 결과를 텍스트로 변환
        analysis_text = ""
        for i, analysis in enumerate(analyses):
            analysis_text += f"\n문서 {i+1}:\n"
            for key, value in analysis.items():
                if key not in ['document_index', 'text']:
                    analysis_text += f"- {key}: {value}\n"
        
        prompt = f"""
다음 클러스터의 개별 문서 분석 결과를 종합하여 클러스터 전체 요약을 제공해주세요.

클러스터: {cluster_name}
주제: {topic_name}

개별 분석 결과:
{analysis_text}

다음 JSON 구조로 클러스터 전체 요약을 제공해주세요:
{{
    "주요_원인": "클러스터 전체의 주요 원인",
    "주요_행위자": "클러스터에서 나타나는 주요 행위자들",
    "공통_요구사항": "클러스터 전체의 공통 요구사항",
    "전체_톤": "클러스터 전체의 톤",
    "주요_리스크": "클러스터에서 나타나는 주요 리스크",
    "해결_우선순위": "해결이 필요한 우선순위",
    "정책_개선점": "정책 개선을 위한 제안사항"
}}

JSON만 응답해주세요.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_config['model'],
                messages=[
                    {"role": "system", "content": "당신은 상담 데이터 클러스터를 분석하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.llm_config['max_tokens'],
                temperature=self.llm_config['temperature']
            )
            
            result_text = response.choices[0].message.content
            return self._parse_analysis_result(result_text)
            
        except Exception as e:
            print(f"클러스터 요약 실패: {e}")
            return self._create_default_cluster_summary()
    
    def _create_default_cluster_summary(self) -> Dict[str, Any]:
        """기본 클러스터 요약"""
        return {
            "주요_원인": "분석 실패",
            "주요_행위자": "분석 실패",
            "공통_요구사항": "분석 실패",
            "전체_톤": "중립적",
            "주요_리스크": "분석 실패",
            "해결_우선순위": "분석 실패",
            "정책_개선점": "분석 실패"
        }
    
    def save_analysis_results(self, analysis_results: List[Dict[str, Any]], output_dir: str):
        """분석 결과를 저장합니다."""
        # 개별 분석 결과 저장
        individual_results = []
        cluster_summaries = []
        
        for result in analysis_results:
            # 개별 분석 결과
            for analysis in result['individual_analyses']:
                individual_results.append({
                    'cluster_name': result['cluster_name'],
                    'topic_name': result['topic_name'],
                    'document_index': analysis['document_index'],
                    'text': analysis['text'],
                    **{k: v for k, v in analysis.items() if k not in ['document_index', 'text']}
                })
            
            # 클러스터 요약
            cluster_summaries.append({
                'cluster_name': result['cluster_name'],
                'topic_name': result['topic_name'],
                **result['cluster_summary']
            })
        
        # CSV 파일로 저장
        individual_df = pd.DataFrame(individual_results)
        individual_df.to_csv(f"{output_dir}/individual_analyses.csv", index=False, encoding='utf-8-sig')
        
        cluster_summary_df = pd.DataFrame(cluster_summaries)
        cluster_summary_df.to_csv(f"{output_dir}/cluster_analyses.csv", index=False, encoding='utf-8-sig')
        
        # JSON 파일로 저장
        with open(f"{output_dir}/analysis_results.json", 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        print(f"분석 결과 저장 완료: {output_dir}") 