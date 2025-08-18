# 대규모 상담/게시판 데이터 주제 발견 및 심층 분석 자동화

## 📋 프로젝트 개요

이 프로젝트는 대규모 상담/게시판 데이터(약 10,000행)에서 자동으로 주제를 발견하고, 주제별로 심층 분석을 수행하여 정책/운영 개선 인사이트를 도출하는 자동화 파이프라인입니다.

### 주요 기능
- **전체 주제 발견**: LDA, NMF, BERTopic 등을 활용한 자동 주제 추출
- **주제별 심층 분석**: 임베딩 기반 클러스터링 및 LLM 분석
- **자동 리포트 생성**: CSV, Markdown, 시각화 결과물 자동 생성

## 🏗️ 프로젝트 구조

```
Bulletin_board_analysis/
├── config.yaml                 # 프로젝트 설정 파일
├── data_sample.xlsx            # 샘플 데이터
├── requirements.txt            # 필요한 패키지 목록
├── run_all.py                  # 전체 파이프라인 실행
├── run_01_data_preprocessing.py    # 데이터 전처리
├── run_02_topic_discovery.py       # 주제 발견
├── run_03_clustering.py            # 클러스터링
├── run_04_llm_analysis.py          # LLM 분석
├── run_05_report_generation.py     # 리포트 생성
├── src/                        # 소스 코드
│   ├── ingest/                 # 데이터 수집/전처리
│   │   └── data_loader.py
│   ├── topics/                 # 주제 발견
│   │   └── topic_discovery.py
│   ├── cluster/                # 클러스터링
│   │   └── document_clustering.py
│   ├── llm/                    # LLM 분석
│   │   └── llm_analyzer.py
│   ├── report/                 # 리포트 생성
│   │   └── report_generator.py
│   └── utils/                  # 유틸리티
│       ├── config.py
│       └── text_processing.py
└── outputs/                    # 결과물
    ├── csv/                    # CSV 파일들
    ├── reports/                # 리포트 파일들
    └── visualizations/         # 시각화 파일들
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 2. 설정 파일 수정

`config.yaml` 파일에서 다음 설정을 확인/수정하세요:

```yaml
# 데이터 설정
data:
  input_file: "data_sample.xlsx"  # 입력 파일명

# LLM 설정 (OpenAI API 사용 시)
llm:
  model: "gpt-3.5-turbo"
  # OPENAI_API_KEY 환경변수 설정 필요
```

### 3. 실행

#### 전체 파이프라인 실행
```bash
python run_all.py
```

#### 단계별 실행
```bash
# 1. 데이터 전처리
python run_01_data_preprocessing.py

# 2. 주제 발견
python run_02_topic_discovery.py

# 3. 클러스터링
python run_03_clustering.py

# 4. LLM 분석 (선택사항)
python run_04_llm_analysis.py

# 5. 리포트 생성
python run_05_report_generation.py
```

## 📊 결과물

### CSV 파일들
- `global_topics_top_terms.csv`: 주제별 상위 키워드
- `topic_assignments.csv`: 문서별 주제 할당
- `cluster_summary.csv`: 클러스터별 요약
- `individual_analyses.csv`: 개별 문서 LLM 분석 결과
- `cluster_analyses.csv`: 클러스터별 LLM 분석 요약

### 시각화
- `topic_distribution.png`: 주제별 문서 수 분포
- `cluster_distribution.png`: 클러스터별 문서 수 분포
- `wordclouds/`: 주제별/클러스터별 워드클라우드
- `frequency_charts/`: 빈도 분석 차트

### 리포트
- `분석_리포트.md`: 최종 분석 리포트 (Markdown)
- `final_statistics.json`: 최종 통계 요약

## 🔧 기술 스택

### 핵심 기술
- **주제 발견**: scikit-learn LDA, NMF
- **임베딩**: Sentence-BERT (paraphrase-multilingual-MiniLM-L12-v2)
- **클러스터링**: K-means with silhouette analysis
- **텍스트 분석**: OpenAI GPT 모델
- **시각화**: matplotlib, seaborn, wordcloud

### 데이터 처리
- **전처리**: pandas, numpy
- **텍스트 정리**: 정규표현식, 개인정보 마스킹
- **품질 관리**: 중복 제거, 길이 필터링

## 📈 분석 파이프라인

### 1. 데이터 전처리
- Excel/CSV 파일 로드
- 텍스트 정리 및 정규화
- 개인정보 마스킹
- 중복 제거 및 품질 관리

### 2. 주제 발견
- CountVectorizer를 사용한 텍스트 벡터화
- LDA 알고리즘으로 주제 모델 학습
- 주제별 상위 키워드 추출
- 문서별 주제 할당

### 3. 클러스터링
- Sentence-BERT로 텍스트 임베딩 생성
- Silhouette 분석으로 최적 클러스터 수 탐색
- K-means 클러스터링 수행
- 클러스터별 대표 문서 선택

### 4. LLM 분석 (선택사항)
- OpenAI GPT 모델을 사용한 텍스트 분석
- 원인, 행위자, 요구사항, 리스크 등 추출
- 클러스터별 요약 및 정책 제언

### 5. 리포트 생성
- 마크다운 형식의 종합 리포트 생성
- 시각화 차트 및 워드클라우드 생성
- CSV 형태의 상세 결과 저장

## ⚙️ 설정 옵션

### 주제 발견 설정
```yaml
topic_discovery:
  algorithm: "lda"  # lda, nmf, bertopic
  n_topics: 10
  min_df: 5
  max_df: 0.4
  top_terms_per_topic: 15
```

### 클러스터링 설정
```yaml
clustering:
  algorithm: "kmeans"
  n_clusters_range: [5, 15]
  embedding_model: "paraphrase-multilingual-MiniLM-L12-v2"
```

### LLM 설정
```yaml
llm:
  model: "gpt-3.5-turbo"
  max_tokens: 1000
  temperature: 0.1
```

## 🔍 사용 예시

### 데이터 형식
입력 데이터는 다음 컬럼을 포함해야 합니다:
- `연번`: 문서 ID
- `상담일자`: 날짜
- `상담유형`: 상담 유형
- `상담요약`: 요약 텍스트
- `상담인 유형`: 상담인 유형
- `상담내용`: 상세 내용

### 실행 결과
```
============================================================
대규모 상담/게시판 데이터 주제 발견 및 심층 분석
전체 파이프라인 실행
============================================================

==================== 단계 1: run_01_data_preprocessing.py ====================
데이터 전처리 파이프라인 시작
==================================================
1. 데이터 로드 중...
데이터 로드 완료: (12, 6)
2. 데이터 전처리 중...
데이터 전처리 시작...
전처리 완료: (10, 8)
3. 전처리된 데이터 저장 중...

전처리 완료:
- 원본 데이터: (12, 6)
- 전처리 후 데이터: (10, 8)
- 제거된 행: 2
- 평균 텍스트 길이: 45.2
- 최소 텍스트 길이: 20
- 최대 텍스트 길이: 89

✅ run_01_data_preprocessing.py 실행 완료
```

## 🛠️ 문제 해결

### 일반적인 문제들

1. **OpenAI API 키 오류**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **한글 폰트 오류**
   - macOS: `/System/Library/Fonts/AppleGothic.ttf`
   - Windows: `C:/Windows/Fonts/malgun.ttf`
   - Linux: `/usr/share/fonts/truetype/nanum/NanumGothic.ttf`

3. **메모리 부족 오류**
   - `config.yaml`에서 `n_topics` 또는 `n_clusters_range` 값을 줄이세요
   - 데이터를 더 작은 배치로 나누어 처리하세요

### 로그 확인
각 스크립트는 상세한 로그를 출력합니다. 오류 발생 시 로그를 확인하여 문제를 파악하세요.

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다!

---

**참고**: LLM 분석 기능을 사용하려면 OpenAI API 키가 필요합니다. API 키는 환경변수 `OPENAI_API_KEY`에 설정하거나, `.env` 파일에 저장하세요. 