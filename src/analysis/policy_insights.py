import pandas as pd
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
import json
from src.utils.text_processing import analyze_ngrams

class PolicyInsights:
    """정책 인사이트 도출 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_config = config['output']
    
    def generate_policy_insights(self, df: pd.DataFrame, topic_results: Dict[str, Any], 
                               cluster_results: Dict[str, Any], output_dir: str):
        """정책 인사이트를 생성합니다."""
        print("정책 인사이트 생성 시작...")
        
        insights = {
            'faq_suggestions': [],
            'education_materials': [],
            'regulation_improvements': [],
            'risk_management': [],
            'priority_actions': []
        }
        
        # 1. FAQ 제안 생성
        insights['faq_suggestions'] = self._generate_faq_suggestions(df, topic_results)
        
        # 2. 교육자료 제안
        insights['education_materials'] = self._generate_education_materials(df, topic_results)
        
        # 3. 규약 개선 제안
        insights['regulation_improvements'] = self._generate_regulation_improvements(df, topic_results)
        
        # 4. 리스크 관리
        insights['risk_management'] = self._generate_risk_management(df, cluster_results)
        
        # 5. 우선순위 액션
        insights['priority_actions'] = self._generate_priority_actions(df, insights)
        
        # 결과 저장
        self._save_insights(insights, output_dir)
        
        return insights
    
    def _generate_faq_suggestions(self, df: pd.DataFrame, topic_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """FAQ 제안을 생성합니다."""
        faq_suggestions = []
        
        # 상담유형별 FAQ 제안
        consultation_freq = df['상담유형'].value_counts()
        
        for consultation_type, count in consultation_freq.items():
            if count >= 1:  # 1건 이상인 상담유형
                faq = {
                    'category': consultation_type,
                    'question': self._generate_faq_question(consultation_type),
                    'priority': 'High' if count >= 2 else 'Medium',
                    'frequency': int(count)
                }
                faq_suggestions.append(faq)
        
        # 주제별 FAQ 제안
        if 'top_terms' in topic_results:
            for topic_id, terms in topic_results['top_terms'].items():
                topic_keywords = [term for term, _ in terms[:3]]
                faq = {
                    'category': f'Topic {topic_id+1}',
                    'question': f"{' '.join(topic_keywords)} 관련 자주 묻는 질문",
                    'priority': 'High',
                    'frequency': 'Based on topic modeling'
                }
                faq_suggestions.append(faq)
        
        return faq_suggestions
    
    def _generate_faq_question(self, consultation_type: str) -> str:
        """상담유형에 따른 FAQ 질문을 생성합니다."""
        faq_templates = {
            '관리비': '관리비 관련 문의 및 분쟁 해결 방법은?',
            '관리규약': '관리규약 제정 및 개정 절차는?',
            '분쟁': '분쟁 발생 시 해결 절차는?',
            '의결권': '총회에서의 의결권 행사 방법은?',
            '회계감사': '회계감사 대상 및 절차는?',
            '선거': '입주자대표 선거 절차는?',
            '기타': '기타 상담 사항 처리 방법은?'
        }
        
        return faq_templates.get(consultation_type, f'{consultation_type} 관련 자주 묻는 질문')
    
    def _generate_education_materials(self, df: pd.DataFrame, topic_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """교육자료 제안을 생성합니다."""
        education_materials = []
        
        # 상담인 유형별 교육자료
        person_type_freq = df['상담인 유형'].value_counts()
        
        for person_type, count in person_type_freq.items():
            if count >= 1:
                material = {
                    'target': person_type,
                    'title': f'{person_type} 대상 교육자료',
                    'content': self._generate_education_content(person_type),
                    'priority': 'High' if count >= 2 else 'Medium'
                }
                education_materials.append(material)
        
        # 주제별 교육자료
        if 'top_terms' in topic_results:
            for topic_id, terms in topic_results['top_terms'].items():
                topic_keywords = [term for term, _ in terms[:3]]
                material = {
                    'target': f'Topic {topic_id+1}',
                    'title': f"{' '.join(topic_keywords)} 관련 교육자료",
                    'content': f"{' '.join(topic_keywords)} 관련 법령 및 처리 절차 안내",
                    'priority': 'High'
                }
                education_materials.append(material)
        
        return education_materials
    
    def _generate_education_content(self, person_type: str) -> str:
        """상담인 유형에 따른 교육 내용을 생성합니다."""
        content_templates = {
            '관리소장': '관리소 운영 관련 법령, 분쟁 해결 방법, 의사소통 기법',
            '점유자': '입주자 권리와 의무, 상담 신청 방법, 분쟁 해결 절차',
            '구분소유자': '소유권 관련 법령, 총회 참여 방법, 의결권 행사',
            '기타': '일반적인 상담 절차 및 관련 법령 안내'
        }
        
        return content_templates.get(person_type, f'{person_type} 대상 기본 교육 내용')
    
    def _generate_regulation_improvements(self, df: pd.DataFrame, topic_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """규약 개선 제안을 생성합니다."""
        improvements = []
        
        # 상담유형별 규약 개선 제안
        consultation_freq = df['상담유형'].value_counts()
        
        for consultation_type, count in consultation_freq.items():
            if count >= 1:
                improvement = {
                    'area': consultation_type,
                    'suggestion': self._generate_regulation_suggestion(consultation_type),
                    'priority': 'High' if count >= 2 else 'Medium',
                    'reason': f'{consultation_type} 관련 상담이 {count}건으로 많음'
                }
                improvements.append(improvement)
        
        return improvements
    
    def _generate_regulation_suggestion(self, consultation_type: str) -> str:
        """상담유형에 따른 규약 개선 제안을 생성합니다."""
        suggestion_templates = {
            '관리비': '관리비 산정 기준 및 인상 절차에 대한 명확한 규정 추가',
            '관리규약': '관리규약 제정 및 개정 절차에 대한 상세 규정 보완',
            '분쟁': '분쟁 해결 절차 및 중재 방법에 대한 규정 신설',
            '의결권': '총회 의결권 행사 방법 및 대리인 선임 절차 명확화',
            '회계감사': '회계감사 대상 및 절차에 대한 상세 규정 추가',
            '선거': '입주자대표 선거 절차 및 자격 요건 명확화',
            '기타': '기타 상담 사항 처리에 대한 일반 규정 보완'
        }
        
        return suggestion_templates.get(consultation_type, f'{consultation_type} 관련 규정 보완 필요')
    
    def _generate_risk_management(self, df: pd.DataFrame, cluster_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """리스크 관리 제안을 생성합니다."""
        risk_management = []
        
        # 상담유형별 리스크 분석
        consultation_freq = df['상담유형'].value_counts()
        
        for consultation_type, count in consultation_freq.items():
            if count >= 2:  # 2건 이상인 경우 리스크로 분류
                risk = {
                    'risk_area': consultation_type,
                    'risk_level': 'High' if count >= 3 else 'Medium',
                    'description': f'{consultation_type} 관련 상담이 {count}건으로 분쟁 위험 높음',
                    'mitigation': f'{consultation_type} 관련 선제적 대응 체계 구축 필요'
                }
                risk_management.append(risk)
        
        # 클러스터별 리스크 분석
        if 'cluster_stats' in cluster_results:
            for _, cluster in cluster_results['cluster_stats'].iterrows():
                if cluster['document_count'] >= 2:
                    risk = {
                        'risk_area': f"Cluster {cluster['cluster_name']}",
                        'risk_level': 'High' if cluster['document_count'] >= 3 else 'Medium',
                        'description': f"클러스터 {cluster['cluster_name']}에서 {cluster['document_count']}건의 유사한 문제 발생",
                        'mitigation': f"클러스터 {cluster['cluster_name']} 관련 표준 대응 절차 수립 필요"
                    }
                    risk_management.append(risk)
        
        return risk_management
    
    def _generate_priority_actions(self, df: pd.DataFrame, insights: Dict[str, Any]) -> List[Dict[str, str]]:
        """우선순위 액션을 생성합니다."""
        priority_actions = []
        
        # 상담 빈도 기반 우선순위
        consultation_freq = df['상담유형'].value_counts()
        person_freq = df['상담인 유형'].value_counts()
        
        # 상위 3개 상담유형에 대한 즉시 대응
        for i, (consultation_type, count) in enumerate(consultation_freq.head(3).items()):
            priority = 'Immediate' if i == 0 else 'High' if i == 1 else 'Medium'
            action = {
                'action': f'{consultation_type} 관련 대응 체계 구축',
                'priority': priority,
                'timeline': '1-2개월' if priority == 'Immediate' else '3-6개월',
                'reason': f'{consultation_type} 상담이 {count}건으로 가장 많음'
            }
            priority_actions.append(action)
        
        # 상담인 유형별 맞춤 대응
        for i, (person_type, count) in enumerate(person_freq.head(2).items()):
            action = {
                'action': f'{person_type} 대상 맞춤 대응 전략 수립',
                'priority': 'High' if i == 0 else 'Medium',
                'timeline': '2-3개월',
                'reason': f'{person_type} 상담이 {count}건으로 많음'
            }
            priority_actions.append(action)
        
        return priority_actions
    
    def _save_insights(self, insights: Dict[str, Any], output_dir: str):
        """인사이트를 파일로 저장합니다."""
        output_path = Path(output_dir)
        
        # JSON 형태로 저장
        with open(output_path / "policy_insights.json", 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)
        
        # CSV 형태로도 저장
        for key, data in insights.items():
            if data and isinstance(data, list):
                df = pd.DataFrame(data)
                df.to_csv(output_path / f"{key}.csv", index=False, encoding='utf-8-sig')
        
        print(f"정책 인사이트 저장 완료: {output_path}") 