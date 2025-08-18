# 대규모 상담/게시판 데이터 주제 발견 및 심층 분석 파이프라인

## 전체 분석 과정 다이어그램

```mermaid
graph TB
    %% 입력 데이터
    A[📊 data_sample.xlsx<br/>원본 상담 데이터] --> B[🔧 데이터 전처리]
    
    %% 데이터 전처리 단계
    B --> B1[📥 데이터 로드<br/>Excel 파일 읽기]
    B1 --> B2[🧹 텍스트 정리<br/>특수문자 제거, 정규화]
    B2 --> B3[🔗 텍스트 결합<br/>상담요약 + 상담내용]
    B3 --> B4[📏 길이 필터링<br/>최소 20자 이상]
    B4 --> B5[🔄 중복 제거<br/>동일 텍스트 제거]
    B5 --> C[💾 전처리된 데이터<br/>preprocessed_data.csv]
    
    %% 주제 발견 단계
    C --> D[🔍 주제 발견<br/>LDA 모델]
    D --> D1[📝 텍스트 벡터화<br/>TF-IDF 변환]
    D1 --> D2[🎯 LDA 모델 학습<br/>주제 수 자동 탐색]
    D2 --> D3[🏷️ 주제 할당<br/>문서별 주제 분류]
    D3 --> D4[📊 주제별 키워드<br/>상위 10개 단어]
    D4 --> E[📈 주제 발견 결과<br/>topic_assignments.csv<br/>global_topics_top_terms.csv]
    
    %% 클러스터링 단계
    C --> F[🎯 문서 클러스터링<br/>K-means + 임베딩]
    F --> F1[🧠 텍스트 임베딩<br/>multilingual-MiniLM]
    F1 --> F2[🔢 차원 축소<br/>PCA/UMAP]
    F2 --> F3[🎯 K-means 클러스터링<br/>최적 클러스터 수 탐색]
    F3 --> F4[📊 클러스터 분석<br/>대표 문서 선정]
    F4 --> G[📊 클러스터링 결과<br/>cluster_assignments.csv<br/>cluster_summary.csv]
    
    %% LLM 분석 단계
    G --> H[🤖 LLM 심층 분석<br/>GPT-3.5-turbo]
    H --> H1[📋 클러스터별 텍스트 수집<br/>대표 문서 선별]
    H1 --> H2[🔍 주요 원인 분석<br/>상담 발생 배경]
    H2 --> H3[👥 주요 행위자 식별<br/>관련자 분석]
    H3 --> H4[💡 정책 개선점 도출<br/>해결 방안 제시]
    H4 --> I[📋 LLM 분석 결과<br/>analysis_results.json]
    
    %% 리포트 생성 단계
    E --> J[📄 최종 리포트 생성]
    G --> J
    I --> J
    J --> J1[📊 통계 분석<br/>빈도수, 교차분석]
    J1 --> J2[📈 시각화 생성<br/>워드클라우드, 차트]
    J2 --> J3[📝 마크다운 리포트<br/>분석_리포트.md]
    J3 --> K[📁 최종 결과물<br/>outputs/]
    
    %% 출력 결과물
    K --> L1[📊 CSV 파일들<br/>분석 결과 데이터]
    K --> L2[📈 시각화 파일들<br/>차트, 워드클라우드]
    K --> L3[📄 분석 리포트<br/>마크다운 문서]
    K --> L4[📋 통계 요약<br/>final_statistics.json]
    
    %% 스타일 정의
    classDef inputStyle fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef processStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef outputStyle fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef dataStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class A inputStyle
    class B,B1,B2,B3,B4,B5,D,D1,D2,D3,D4,F,F1,F2,F3,F4,H,H1,H2,H3,H4,J,J1,J2,J3 processStyle
    class C,E,G,I,K outputStyle
    class L1,L2,L3,L4 dataStyle
```

## 상세 분석 단계별 설명

### 1. 🔧 데이터 전처리 단계
- **입력**: `data_sample.xlsx` (원본 상담 데이터)
- **처리 과정**:
  - 텍스트 정리 (특수문자, 불용어 제거)
  - 텍스트 결합 (상담요약 + 상담내용)
  - 길이 필터링 (최소 20자)
  - 중복 제거
- **출력**: `preprocessed_data.csv`

### 2. 🔍 주제 발견 단계
- **입력**: 전처리된 텍스트 데이터
- **처리 과정**:
  - TF-IDF 벡터화
  - LDA 모델 학습 (주제 수 자동 탐색)
  - 문서별 주제 할당
  - 주제별 키워드 추출
- **출력**: `topic_assignments.csv`, `global_topics_top_terms.csv`

### 3. 🎯 문서 클러스터링 단계
- **입력**: 전처리된 텍스트 데이터
- **처리 과정**:
  - 다국어 임베딩 생성 (multilingual-MiniLM)
  - 차원 축소 (PCA/UMAP)
  - K-means 클러스터링 (최적 클러스터 수 탐색)
  - 클러스터별 대표 문서 선정
- **출력**: `cluster_assignments.csv`, `cluster_summary.csv`

### 4. 🤖 LLM 심층 분석 단계
- **입력**: 클러스터링 결과
- **처리 과정**:
  - 클러스터별 대표 텍스트 수집
  - GPT-3.5-turbo를 통한 심층 분석
  - 주요 원인, 행위자, 정책 개선점 도출
- **출력**: `analysis_results.json`

### 5. 📄 최종 리포트 생성 단계
- **입력**: 모든 분석 결과
- **처리 과정**:
  - 통계 분석 및 교차분석
  - 시각화 생성 (워드클라우드, 차트)
  - 마크다운 리포트 생성
- **출력**: `분석_리포트.md`, 시각화 파일들

## 기술 스택

```mermaid
graph LR
    A[📊 데이터 처리] --> A1[pandas]
    A --> A2[numpy]
    
    B[🔍 텍스트 분석] --> B1[scikit-learn]
    B --> B2[gensim]
    B --> B3[konlpy]
    
    C[🧠 딥러닝] --> C1[sentence-transformers]
    C --> C2[torch]
    
    D[🤖 LLM] --> D1[openai]
    D --> D2[GPT-3.5-turbo]
    
    E[📈 시각화] --> E1[matplotlib]
    E --> E2[seaborn]
    E --> E3[wordcloud]
    
    F[⚙️ 유틸리티] --> F1[PyYAML]
    F --> F2[pathlib]
    F --> F3[json]
    
    classDef techStyle fill:#f0f8ff,stroke:#4169e1,stroke-width:2px
    class A1,A2,B1,B2,B3,C1,C2,D1,D2,E1,E2,E3,F1,F2,F3 techStyle
```

## 출력 결과물 구조

```
outputs/
├── csv/
│   ├── preprocessed_data.csv          # 전처리된 데이터
│   ├── topic_assignments.csv          # 주제 할당 결과
│   ├── global_topics_top_terms.csv    # 주제별 키워드
│   ├── cluster_assignments.csv        # 클러스터 할당 결과
│   ├── cluster_summary.csv            # 클러스터 요약
│   └── analysis_results.json          # LLM 분석 결과
├── visualizations/
│   ├── wordclouds/                    # 워드클라우드
│   ├── frequency_charts/              # 빈도수 차트
│   └── cluster_distribution.png       # 클러스터 분포
└── reports/
    ├── 분석_리포트.md                  # 최종 분석 리포트
    └── final_statistics.json          # 통계 요약
```

## 실행 방법

```bash
# 전체 파이프라인 실행
python run_all.py

# 개별 단계 실행
python run_01_data_preprocessing.py    # 데이터 전처리
python run_02_topic_discovery.py       # 주제 발견
python run_03_clustering.py            # 클러스터링
python run_04_llm_analysis.py          # LLM 분석
python run_05_report_generation.py     # 리포트 생성
``` 