import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List
from pathlib import Path
import json
from src.utils.plotting import setup_korean_font, get_korean_font_prop

class CrossAnalysis:
    """교차 분석 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_config = config['output']
    
    def analyze_consultation_patterns(self, df: pd.DataFrame, output_dir: str):
        """상담 패턴을 분석합니다."""
        print("상담 패턴 분석 시작...")
        
        # 1. 상담인 유형별 상담유형 교차표
        cross_table = pd.crosstab(df['상담인 유형'], df['상담유형'], margins=True)
        cross_table.to_csv(f"{output_dir}/상담인유형_상담유형_교차표.csv", encoding='utf-8-sig')
        
        # 2. 상담인 유형별 빈도
        person_type_freq = df['상담인 유형'].value_counts()
        person_type_freq.to_csv(f"{output_dir}/상담인유형_빈도수.csv", encoding='utf-8-sig')
        
        # 3. 상담유형별 빈도
        consultation_type_freq = df['상담유형'].value_counts()
        consultation_type_freq.to_csv(f"{output_dir}/상담유형_빈도수.csv", encoding='utf-8-sig')
        
        # 4. 시각화
        self._create_cross_analysis_visualizations(df, output_dir)
        
        # 5. 인사이트 생성
        insights = self._generate_insights(df)
        
        return {
            'cross_table': cross_table,
            'person_type_freq': person_type_freq,
            'consultation_type_freq': consultation_type_freq,
            'insights': insights
        }
    
    def _create_cross_analysis_visualizations(self, df: pd.DataFrame, output_dir: str):
        """교차 분석 시각화를 생성합니다."""
        output_path = Path(output_dir)
        visualizations_path = output_path.parent / "visualizations"
        visualizations_path.mkdir(exist_ok=True)
        
        # 한글 폰트 설정
        setup_korean_font()
        font_prop = get_korean_font_prop()
        
        # 1. 상담인 유형별 상담유형 히트맵
        plt.figure(figsize=(12, 8))
        cross_table = pd.crosstab(df['상담인 유형'], df['상담유형'])
        sns.heatmap(cross_table, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Number of Consultations'})
        plt.title('상담인 유형별 상담유형 히트맵', fontproperties=font_prop, fontsize=16)
        plt.xlabel('상담유형', fontproperties=font_prop, fontsize=12)
        plt.ylabel('상담인 유형', fontproperties=font_prop, fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{visualizations_path}/consultation_pattern_heatmap.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 상담인 유형별 빈도 차트
        plt.figure(figsize=(10, 6))
        person_type_freq = df['상담인 유형'].value_counts()
        sns.barplot(x=person_type_freq.values, y=person_type_freq.index)
        plt.title('상담인 유형별 상담 빈도', fontproperties=font_prop, fontsize=16)
        plt.xlabel('상담 건수', fontproperties=font_prop, fontsize=12)
        plt.ylabel('상담인 유형', fontproperties=font_prop, fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{visualizations_path}/person_type_frequency.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 상담유형별 빈도 차트
        plt.figure(figsize=(10, 6))
        consultation_type_freq = df['상담유형'].value_counts()
        sns.barplot(x=consultation_type_freq.values, y=consultation_type_freq.index)
        plt.title('상담유형별 상담 빈도', fontproperties=font_prop, fontsize=16)
        plt.xlabel('상담 건수', fontproperties=font_prop, fontsize=12)
        plt.ylabel('상담유형', fontproperties=font_prop, fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{visualizations_path}/consultation_type_frequency.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"교차 분석 시각화 저장 완료: {visualizations_path}")
    
    def _generate_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """상담 패턴 인사이트를 생성합니다."""
        insights = {
            'top_consultation_types': [],
            'top_person_types': [],
            'key_patterns': [],
            'recommendations': []
        }
        
        # 상위 상담유형
        consultation_freq = df['상담유형'].value_counts()
        insights['top_consultation_types'] = consultation_freq.head(3).to_dict()
        
        # 상위 상담인 유형
        person_freq = df['상담인 유형'].value_counts()
        insights['top_person_types'] = person_freq.head(3).to_dict()
        
        # 주요 패턴 분석
        cross_table = pd.crosstab(df['상담인 유형'], df['상담유형'])
        
        # 각 상담인 유형별 주요 상담유형
        for person_type in cross_table.index:
            if person_type != 'All':
                top_consultation = cross_table.loc[person_type].idxmax()
                count = cross_table.loc[person_type, top_consultation]
                insights['key_patterns'].append({
                    'person_type': person_type,
                    'main_consultation': top_consultation,
                    'count': int(count)
                })
        
        # 정책 제언
        insights['recommendations'] = self._generate_recommendations(df, insights)
        
        return insights
    
    def _generate_recommendations(self, df: pd.DataFrame, insights: Dict[str, Any]) -> List[str]:
        """정책 제언을 생성합니다."""
        recommendations = []
        
        # 상담유형별 제언
        consultation_freq = df['상담유형'].value_counts()
        top_consultation = consultation_freq.index[0]
        
        if '관리비' in top_consultation:
            recommendations.append("관리비 관련 상담이 가장 많으므로 관리비 정책 가이드라인 강화 필요")
        elif '분쟁' in top_consultation:
            recommendations.append("분쟁 관련 상담이 많으므로 분쟁 조기 해결 체계 구축 필요")
        elif '관리규약' in top_consultation:
            recommendations.append("관리규약 관련 상담이 많으므로 규약 해설서 및 교육 자료 개발 필요")
        
        # 상담인 유형별 제언
        person_freq = df['상담인 유형'].value_counts()
        top_person = person_freq.index[0]
        
        if '관리소장' in top_person:
            recommendations.append("관리소장의 상담이 많으므로 관리소장 대상 교육 프로그램 강화")
        elif '점유자' in top_person:
            recommendations.append("점유자 상담이 많으므로 점유자 대상 정보 제공 체계 개선")
        
        # 교차 패턴 제언
        for pattern in insights['key_patterns']:
            if pattern['count'] >= 2:  # 2건 이상인 패턴만
                recommendations.append(
                    f"{pattern['person_type']}의 {pattern['main_consultation']} 관련 상담이 {pattern['count']}건으로 많으므로 "
                    f"해당 유형별 맞춤 대응 방안 수립 필요"
                )
        
        return recommendations 