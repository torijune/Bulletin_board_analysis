# 대규모 상담/게시판 데이터 주제 발견 및 심층 분석

상담 데이터를 분석하여 주제를 발견하고, 각 주제별로 상세한 분석을 수행하는 종합적인 데이터 분석 파이프라인입니다.

## 🚀 주요 기능

### 📊 **데이터 분석 파이프라인**
1. **데이터 전처리**: 텍스트 정리, 중복 제거, 길이 필터링
2. **주제 발견**: LDA를 통한 자동 주제 탐색 및 할당
3. **문서 클러스터링**: 임베딩 기반 K-means 클러스터링
4. **LLM 심층 분석**: GPT-3.5-turbo를 통한 상세 분석
5. **리포트 생성**: 마크다운 형태의 종합 분석 리포트
6. **주제별 상세 분석**: 각 주제별 워드클라우드 및 LLM 분석

### 🎯 **주요 특징**
- **Clean Architecture**: 모듈화된 구조로 유지보수성 향상
- **대용량 데이터 지원**: 샘플링 및 최적화 기능
- **자동화된 워크플로우**: 한 번의 실행으로 전체 분석 완료
- **다양한 결과물**: CSV, JSON, 시각화, 리포트 등
- **LLM 통합**: GPT-3.5-turbo를 통한 지능형 분석

## 📁 프로젝트 구조

```
Bulletin_board_analysis/
├── src/                    # 소스 코드
│   ├── ingest/            # 데이터 로딩
│   ├── topics/            # 주제 발견
│   ├── cluster/           # 클러스터링
│   ├── llm/               # LLM 분석
│   ├── report/            # 리포트 생성
│   ├── analysis/          # 추가 분석
│   └── utils/             # 유틸리티
├── outputs/               # 결과물 저장
├── run_all.py            # 메인 실행 스크립트
├── run_topic_analysis.py # 주제별 분석 (별도)
├── config.yaml           # 설정 파일
├── requirements.txt      # 의존성
├── README.md            # 프로젝트 설명
├── .gitignore           # Git 제외 파일
└── data_sample.xlsx     # 샘플 데이터
```

## 🛠️ 설치 및 설정

### 1. 저장소 클론
```bash
git clone https://github.com/torijune/Bulletin_board_analysis.git
cd Bulletin_board_analysis
```

### 2. 가상환경 생성 및 패키지 설치
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env` 파일을 생성하고 OpenAI API 키를 설정하세요:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 사용 방법

### 전체 파이프라인 실행
```bash
python run_all.py
```

### 특정 단계만 실행
```bash
# 개별 단계 실행
python run_all.py --step preprocessing
python run_all.py --step topic
python run_all.py --step clustering
python run_all.py --step llm
python run_all.py --step report
python run_all.py --step topic-analysis

# 특정 단계들만 실행
python run_all.py --steps topic clustering llm

# 주제별 상세 분석 제외하고 실행
python run_all.py --skip-topic-analysis
```

### 주제별 상세 분석만 실행
```bash
python run_topic_analysis.py
```

## 📊 결과물

### 📁 출력 디렉토리 구조
```
outputs/
├── csv/                   # CSV 파일들
│   ├── preprocessed_data.csv
│   ├── topic_assignments.csv
│   ├── global_topics_top_terms.csv
│   ├── cluster_assignments.csv
│   ├── analysis_results.json
│   └── topic_analyses.json
├── visualizations/        # 시각화 파일들
│   ├── topic_distribution.png
│   └── cluster_distribution.png
├── wordclouds/           # 워드클라우드
│   ├── topic_0_wordcloud.png
│   └── topic_1_wordcloud.png
└── reports/              # 리포트 파일들
    ├── 분석_리포트.md
    └── topic_analysis_report.md
```

### 📋 주요 결과물
- **주제 발견 결과**: 발견된 주제들과 문서별 할당
- **클러스터링 결과**: 문서 클러스터와 대표 문서
- **LLM 분석 결과**: 상세한 문제점, 해결방안, 정책 시사점
- **주제별 상세 분석**: 각 주제별 워드클라우드와 심층 분석
- **종합 리포트**: 마크다운 형태의 분석 리포트

## ⚙️ 설정

`config.yaml` 파일에서 분석 파라미터를 조정할 수 있습니다:

```yaml
# 주제 발견 설정
topic_discovery:
  algorithm: "lda"
  n_topics: 3
  auto_find_topics: true
  
# 대용량 데이터 처리 설정
large_scale:
  enabled: false
  sample_size: 1000
  use_keyword_naming: true

# LLM 설정
llm:
  model: "gpt-3.5-turbo"
  max_tokens: 1000
  temperature: 0.1
```

## 🔧 유틸리티

### 결과 확인
```bash
python -c "from src.utils.check_utils import check_all_results; check_all_results('outputs')"
```

### 데이터 무결성 검사
```bash
python -c "from src.utils.check_utils import check_data_integrity; check_data_integrity('data_sample.xlsx')"
```

## 📈 성능 최적화

### 대용량 데이터 처리
만 개 이상의 데이터를 처리할 때는 `config.yaml`에서 대용량 모드를 활성화하세요:

```yaml
topic_discovery:
  large_scale:
    enabled: true
    sample_size: 2000
    use_keyword_naming: true
```

### 예상 성능
- **1,000개 문서**: 10-30분
- **10,000개 문서**: 1-2시간 (대용량 모드 사용 시)
- **메모리 사용량**: 2-4GB (대용량 모드)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.

---

**🎉 이 프로젝트로 상담 데이터에서 의미 있는 인사이트를 발견하세요!** 