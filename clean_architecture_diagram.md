# Clean Architecture 구조 다이어그램

## 프로젝트 아키텍처

```mermaid
graph TB
    %% 외부 레이어 (Infrastructure)
    subgraph "🌐 Infrastructure Layer"
        A1[📁 data_sample.xlsx<br/>원본 데이터]
        A2[📄 config.yaml<br/>설정 파일]
        A3[📊 outputs/<br/>결과 저장소]
        A4[🤖 OpenAI API<br/>GPT-3.5-turbo]
    end
    
    %% 인터페이스 레이어 (Interface)
    subgraph "🔌 Interface Layer"
        B1[📥 DataLoader<br/>데이터 로딩 인터페이스]
        B2[🔍 TopicDiscovery<br/>주제 발견 인터페이스]
        B3[🎯 DocumentClustering<br/>클러스터링 인터페이스]
        B4[🤖 LLMAnalyzer<br/>LLM 분석 인터페이스]
        B5[📄 ReportGenerator<br/>리포트 생성 인터페이스]
    end
    
    %% 애플리케이션 레이어 (Application)
    subgraph "⚙️ Application Layer"
        C1[📋 DataService<br/>데이터 처리 서비스]
        C2[🔍 TopicService<br/>주제 발견 서비스]
        C3[🎯 ClusteringService<br/>클러스터링 서비스]
        C4[🤖 AnalysisService<br/>분석 서비스]
        C5[📄 ReportService<br/>리포트 서비스]
    end
    
    %% 도메인 레이어 (Domain)
    subgraph "🏛️ Domain Layer"
        D1[📊 Data<br/>데이터 엔티티]
        D2[🔍 Topic<br/>주제 엔티티]
        D3[🎯 Cluster<br/>클러스터 엔티티]
        D4[🤖 Analysis<br/>분석 엔티티]
        D5[📄 Report<br/>리포트 엔티티]
    end
    
    %% 유틸리티 레이어 (Utils)
    subgraph "🛠️ Utils Layer"
        E1[⚙️ Config<br/>설정 관리]
        E2[📈 Plotting<br/>시각화 유틸]
        E3[📝 TextProcessing<br/>텍스트 처리]
    end
    
    %% 실행 스크립트
    subgraph "🚀 Execution Scripts"
        F1[run_01_data_preprocessing.py]
        F2[run_02_topic_discovery.py]
        F3[run_03_clustering.py]
        F4[run_04_llm_analysis.py]
        F5[run_05_report_generation.py]
        F6[run_all.py]
    end
    
    %% 연결 관계
    A1 --> B1
    A2 --> E1
    A3 --> B5
    A4 --> B4
    
    B1 --> C1
    B2 --> C2
    B3 --> C3
    B4 --> C4
    B5 --> C5
    
    C1 --> D1
    C2 --> D2
    C3 --> D3
    C4 --> D4
    C5 --> D5
    
    E1 --> C1
    E1 --> C2
    E1 --> C3
    E1 --> C4
    E1 --> C5
    
    E2 --> C5
    E3 --> C1
    E3 --> C2
    
    F1 --> B1
    F2 --> B2
    F3 --> B3
    F4 --> B4
    F5 --> B5
    F6 --> F1
    F6 --> F2
    F6 --> F3
    F6 --> F4
    F6 --> F5
    
    %% 스타일 정의
    classDef infraStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef interfaceStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef appStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef domainStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef utilsStyle fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef scriptStyle fill:#fce4ec,stroke:#ad1457,stroke-width:2px
    
    class A1,A2,A3,A4 infraStyle
    class B1,B2,B3,B4,B5 interfaceStyle
    class C1,C2,C3,C4,C5 appStyle
    class D1,D2,D3,D4,D5 domainStyle
    class E1,E2,E3 utilsStyle
    class F1,F2,F3,F4,F5,F6 scriptStyle
```

## 디렉토리 구조

```mermaid
graph TD
    A[📁 Bulletin_board_analysis/] --> B[📁 src/]
    A --> C[📁 outputs/]
    A --> D[📄 run_*.py]
    A --> E[📄 config.yaml]
    A --> F[📄 data_sample.xlsx]
    
    B --> B1[📁 ingest/]
    B --> B2[📁 topics/]
    B --> B3[📁 cluster/]
    B --> B4[📁 llm/]
    B --> B5[📁 report/]
    B --> B6[📁 utils/]
    B --> B7[📁 analysis/]
    
    B1 --> B1A[📄 data_loader.py]
    B2 --> B2A[📄 topic_discovery.py]
    B3 --> B3A[📄 document_clustering.py]
    B4 --> B4A[📄 llm_analyzer.py]
    B5 --> B5A[📄 report_generator.py]
    B6 --> B6A[📄 config.py]
    B6 --> B6B[📄 plotting.py]
    B6 --> B6C[📄 text_processing.py]
    B7 --> B7A[📄 cross_analysis.py]
    B7 --> B7B[📄 policy_insights.py]
    
    C --> C1[📁 csv/]
    C --> C2[📁 visualizations/]
    C --> C3[📁 reports/]
    
    D --> D1[📄 run_01_data_preprocessing.py]
    D --> D2[📄 run_02_topic_discovery.py]
    D --> D3[📄 run_03_clustering.py]
    D --> D4[📄 run_04_llm_analysis.py]
    D --> D5[📄 run_05_report_generation.py]
    D --> D6[📄 run_all.py]
    
    classDef rootStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:3px
    classDef srcStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef outputStyle fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef scriptStyle fill:#fce4ec,stroke:#ad1457,stroke-width:2px
    classDef configStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    
    class A rootStyle
    class B,B1,B2,B3,B4,B5,B6,B7,B1A,B2A,B3A,B4A,B5A,B6A,B6B,B6C,B7A,B7B srcStyle
    class C,C1,C2,C3 outputStyle
    class D,D1,D2,D3,D4,D5,D6 scriptStyle
    class E,F configStyle
```

## 데이터 흐름 다이어그램

```mermaid
sequenceDiagram
    participant User as 👤 사용자
    participant Script as 🚀 실행 스크립트
    participant Config as ⚙️ 설정 관리
    participant DataLoader as 📥 데이터 로더
    participant TopicDiscovery as 🔍 주제 발견
    participant Clustering as 🎯 클러스터링
    participant LLMAnalyzer as 🤖 LLM 분석
    participant ReportGen as 📄 리포트 생성
    participant Output as 📁 출력 저장소
    
    User->>Script: python run_all.py 실행
    Script->>Config: 설정 파일 로드
    Config-->>Script: 설정 반환
    
    Script->>DataLoader: 데이터 전처리 시작
    DataLoader->>DataLoader: Excel 파일 읽기
    DataLoader->>DataLoader: 텍스트 정리
    DataLoader->>DataLoader: 중복 제거
    DataLoader->>Output: 전처리된 데이터 저장
    DataLoader-->>Script: 전처리 완료
    
    Script->>TopicDiscovery: 주제 발견 시작
    TopicDiscovery->>Output: 전처리된 데이터 로드
    TopicDiscovery->>TopicDiscovery: TF-IDF 벡터화
    TopicDiscovery->>TopicDiscovery: LDA 모델 학습
    TopicDiscovery->>TopicDiscovery: 주제 할당
    TopicDiscovery->>Output: 주제 발견 결과 저장
    TopicDiscovery-->>Script: 주제 발견 완료
    
    Script->>Clustering: 클러스터링 시작
    Clustering->>Output: 전처리된 데이터 로드
    Clustering->>Clustering: 텍스트 임베딩
    Clustering->>Clustering: K-means 클러스터링
    Clustering->>Output: 클러스터링 결과 저장
    Clustering-->>Script: 클러스터링 완료
    
    Script->>LLMAnalyzer: LLM 분석 시작
    LLMAnalyzer->>Output: 클러스터링 결과 로드
    LLMAnalyzer->>LLMAnalyzer: GPT-3.5-turbo 분석
    LLMAnalyzer->>Output: LLM 분석 결과 저장
    LLMAnalyzer-->>Script: LLM 분석 완료
    
    Script->>ReportGen: 리포트 생성 시작
    ReportGen->>Output: 모든 분석 결과 로드
    ReportGen->>ReportGen: 통계 분석
    ReportGen->>ReportGen: 시각화 생성
    ReportGen->>ReportGen: 마크다운 리포트 생성
    ReportGen->>Output: 최종 리포트 저장
    ReportGen-->>Script: 리포트 생성 완료
    
    Script-->>User: 전체 파이프라인 완료
```

## 의존성 관계

```mermaid
graph LR
    %% 핵심 의존성
    A[📄 config.yaml] --> B[⚙️ Config Utils]
    B --> C[📥 DataLoader]
    B --> D[🔍 TopicDiscovery]
    B --> E[🎯 DocumentClustering]
    B --> F[🤖 LLMAnalyzer]
    B --> G[📄 ReportGenerator]
    
    %% 데이터 흐름
    H[📊 data_sample.xlsx] --> C
    C --> I[💾 preprocessed_data.csv]
    I --> D
    I --> E
    
    %% 결과 흐름
    D --> J[📈 topic_results]
    E --> K[📊 cluster_results]
    K --> F
    J --> G
    K --> G
    F --> L[📋 llm_results]
    L --> G
    
    %% 유틸리티 의존성
    M[📈 Plotting Utils] --> G
    N[📝 TextProcessing Utils] --> C
    N --> D
    
    %% 실행 스크립트
    O[🚀 run_all.py] --> P[📄 run_01_data_preprocessing.py]
    O --> Q[📄 run_02_topic_discovery.py]
    O --> R[📄 run_03_clustering.py]
    O --> S[📄 run_04_llm_analysis.py]
    O --> T[📄 run_05_report_generation.py]
    
    P --> C
    Q --> D
    R --> E
    S --> F
    T --> G
    
    %% 스타일 정의
    classDef configStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef dataStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef processStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef resultStyle fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef utilStyle fill:#fce4ec,stroke:#ad1457,stroke-width:2px
    classDef scriptStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class A,B configStyle
    class H,I dataStyle
    class C,D,E,F,G processStyle
    class J,K,L resultStyle
    class M,N utilStyle
    class O,P,Q,R,S,T scriptStyle
```

## 주요 특징

### 🏗️ **Clean Architecture 원칙**
- **의존성 역전**: 고수준 모듈이 저수준 모듈에 의존하지 않음
- **관심사 분리**: 각 레이어가 명확한 책임을 가짐
- **테스트 용이성**: 각 컴포넌트를 독립적으로 테스트 가능

### 🔄 **데이터 흐름**
1. **입력**: `data_sample.xlsx` → `DataLoader`
2. **처리**: 각 분석 모듈이 순차적으로 실행
3. **출력**: `outputs/` 디렉토리에 구조화된 결과 저장

### 🛠️ **확장성**
- 새로운 분석 모듈 추가 용이
- 설정 기반 동작으로 유연성 확보
- 모듈화된 구조로 유지보수 편의성

### 📊 **결과물**
- CSV 파일: 구조화된 데이터
- 시각화: 차트, 워드클라우드
- 리포트: 마크다운 문서
- 통계: JSON 형태의 요약 정보 