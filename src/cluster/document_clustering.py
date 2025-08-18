import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Tuple
import json
from src.utils.plotting import setup_korean_font, get_korean_font_prop

class DocumentClustering:
    """문서 클러스터링 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.clustering_config = config['clustering']
        self.embedding_model = None
        self.clustering_model = None
        self.embeddings = None
        
    def load_embedding_model(self):
        """임베딩 모델을 로드합니다."""
        model_name = self.clustering_config['embedding_model']
        print(f"임베딩 모델 로드 중: {model_name}")
        
        try:
            self.embedding_model = SentenceTransformer(model_name)
            print("임베딩 모델 로드 완료")
        except Exception as e:
            print(f"임베딩 모델 로드 실패: {e}")
            # 대체 모델 사용
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("대체 임베딩 모델 사용")
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """텍스트를 임베딩으로 변환합니다."""
        if self.embedding_model is None:
            self.load_embedding_model()
        
        print("텍스트 임베딩 생성 중...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        self.embeddings = embeddings
        print(f"임베딩 생성 완료: {embeddings.shape}")
        
        return embeddings
    
    def find_optimal_k(self, embeddings: np.ndarray, max_k: int = 15) -> int:
        """최적의 클러스터 수를 찾습니다."""
        print("최적 클러스터 수 탐색 중...")
        
        silhouette_scores = []
        k_range = range(2, min(max_k + 1, len(embeddings) // 2))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            if len(np.unique(cluster_labels)) > 1:
                score = silhouette_score(embeddings, cluster_labels)
                silhouette_scores.append(score)
            else:
                silhouette_scores.append(0)
        
        optimal_k = k_range[np.argmax(silhouette_scores)]
        print(f"최적 클러스터 수: {optimal_k}")
        
        return optimal_k
    
    def cluster_documents(self, texts: List[str], topic_id: int = None) -> Dict[str, Any]:
        """문서를 클러스터링합니다."""
        print(f"문서 클러스터링 시작 (주제 {topic_id if topic_id is not None else '전체'})")
        
        # 임베딩 생성
        embeddings = self.create_embeddings(texts)
        
        # 최적 클러스터 수 찾기
        max_k = min(self.clustering_config['n_clusters_range'][1], len(texts) // 3)
        optimal_k = self.find_optimal_k(embeddings, max_k)
        
        # 클러스터링 수행
        algorithm = self.clustering_config['algorithm']
        
        if algorithm == 'kmeans':
            self.clustering_model = KMeans(
                n_clusters=optimal_k,
                random_state=42,
                n_init=10
            )
        else:
            raise ValueError(f"지원하지 않는 클러스터링 알고리즘: {algorithm}")
        
        cluster_labels = self.clustering_model.fit_predict(embeddings)
        
        # 클러스터별 통계 생성
        cluster_stats = self._create_cluster_stats(texts, cluster_labels, embeddings)
        
        return {
            'cluster_labels': cluster_labels,
            'cluster_stats': cluster_stats,
            'embeddings': embeddings,
            'optimal_k': optimal_k
        }
    
    def _create_cluster_stats(self, texts: List[str], cluster_labels: np.ndarray, embeddings: np.ndarray) -> pd.DataFrame:
        """클러스터별 통계를 생성합니다."""
        cluster_stats = []
        
        for cluster_id in np.unique(cluster_labels):
            cluster_mask = cluster_labels == cluster_id
            cluster_texts = [texts[i] for i in range(len(texts)) if cluster_mask[i]]
            cluster_embeddings = embeddings[cluster_mask]
            
            # 클러스터 중심과의 유사도 계산
            cluster_center = cluster_embeddings.mean(axis=0)
            similarities = cosine_similarity(cluster_embeddings, [cluster_center]).flatten()
            
            # 대표 문서 선택 (중심과 가장 유사한 문서)
            representative_idx = np.argmax(similarities)
            representative_text = cluster_texts[representative_idx]
            
            cluster_stats.append({
                'cluster_id': int(cluster_id),
                'cluster_name': f'클러스터_{cluster_id+1}',
                'document_count': len(cluster_texts),
                'avg_similarity': similarities.mean(),
                'representative_text': representative_text,
                'sample_texts': cluster_texts[:3] if len(cluster_texts) >= 3 else cluster_texts
            })
        
        return pd.DataFrame(cluster_stats)
    
    def select_representative_documents(self, texts: List[str], cluster_labels: np.ndarray, 
                                      embeddings: np.ndarray, n_representatives: int = 3) -> List[int]:
        """각 클러스터에서 대표 문서를 선택합니다 (MMR 방식)."""
        print("대표 문서 선택 중...")
        
        representative_indices = []
        
        for cluster_id in np.unique(cluster_labels):
            cluster_mask = cluster_labels == cluster_id
            cluster_indices = np.where(cluster_mask)[0]
            cluster_embeddings = embeddings[cluster_mask]
            
            if len(cluster_indices) == 0:
                continue
            
            # 클러스터 중심 계산
            cluster_center = cluster_embeddings.mean(axis=0)
            
            # 중심과의 유사도 계산
            similarities = cosine_similarity(cluster_embeddings, [cluster_center]).flatten()
            
            # 상위 n개 문서 선택
            top_indices = np.argsort(similarities)[-n_representatives:][::-1]
            selected_indices = [cluster_indices[i] for i in top_indices]
            
            representative_indices.extend(selected_indices)
        
        return representative_indices
    
    def save_cluster_results(self, cluster_results: Dict[str, Any], output_dir: str, topic_id: int = None):
        """클러스터링 결과를 저장합니다."""
        topic_suffix = f"_topic_{topic_id}" if topic_id is not None else ""
        
        # 클러스터 통계 저장
        cluster_stats = cluster_results['cluster_stats']
        cluster_stats.to_csv(f"{output_dir}/cluster_summary{topic_suffix}.csv", 
                           index=False, encoding='utf-8-sig')
        
        # 클러스터 할당 저장
        cluster_assignments = pd.DataFrame({
            'document_id': range(len(cluster_results['cluster_labels'])),
            'cluster_id': cluster_results['cluster_labels'],
            'cluster_name': [f'클러스터_{label+1}' for label in cluster_results['cluster_labels']]
        })
        cluster_assignments.to_csv(f"{output_dir}/cluster_assignments{topic_suffix}.csv", 
                                 index=False, encoding='utf-8-sig')
        
        # 대표 문서 인덱스 저장
        representative_indices = self.select_representative_documents(
            [], cluster_results['cluster_labels'], cluster_results['embeddings']
        )
        
        # numpy int64를 일반 int로 변환
        representative_indices = [int(idx) for idx in representative_indices]
        
        with open(f"{output_dir}/representative_indices{topic_suffix}.json", 'w', encoding='utf-8') as f:
            json.dump(representative_indices, f, ensure_ascii=False, indent=2)
        
        print(f"클러스터링 결과 저장 완료: {output_dir}")
    
    def visualize_clusters(self, cluster_results: Dict[str, Any], output_dir: str, topic_id: int = None):
        """클러스터를 시각화합니다."""
        topic_suffix = f"_topic_{topic_id}" if topic_id is not None else ""
        
        # 클러스터별 문서 수 시각화
        cluster_stats = cluster_results['cluster_stats']
        
        # 한글 폰트 설정
        setup_korean_font()
        font_prop = get_korean_font_prop()
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=cluster_stats, x='cluster_name', y='document_count')
        plt.title(f'클러스터별 문서 수 분포{topic_suffix}', fontproperties=font_prop, fontsize=16)
        plt.xlabel('클러스터', fontproperties=font_prop, fontsize=12)
        plt.ylabel('문서 수', fontproperties=font_prop, fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cluster_distribution{topic_suffix}.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"클러스터 시각화 저장 완료: {output_dir}") 