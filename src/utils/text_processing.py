import re
import pandas as pd
from typing import List, Optional, Tuple, Dict

def clean_text(text: str) -> str:
    """텍스트를 정리합니다."""
    if pd.isna(text):
        return ""
    
    # 기본 정리
    text = str(text).strip()
    
    # 개인정보 마스킹 (전화번호, 차량번호 등)
    text = mask_personal_info(text)
    
    # 특수문자 정리
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def mask_personal_info(text: str) -> str:
    """개인정보를 마스킹합니다."""
    # 전화번호 마스킹
    text = re.sub(r'\d{2,3}-\d{3,4}-\d{4}', '[전화번호]', text)
    text = re.sub(r'\d{10,11}', '[전화번호]', text)
    
    # 차량번호 마스킹
    text = re.sub(r'\d{2,3}[가-힣]\d{4}', '[차량번호]', text)
    
    # 주민등록번호 마스킹
    text = re.sub(r'\d{6}-\d{7}', '[주민번호]', text)
    
    return text

def combine_text_columns(df: pd.DataFrame, text_columns: List[str]) -> pd.Series:
    """여러 텍스트 컬럼을 결합합니다."""
    combined_texts = []
    
    for _, row in df.iterrows():
        text_parts = []
        for col in text_columns:
            if col in df.columns and not pd.isna(row[col]):
                text_parts.append(str(row[col]))
        
        combined_text = ' '.join(text_parts)
        combined_texts.append(combined_text)
    
    return pd.Series(combined_texts, index=df.index)

def filter_by_length(texts: pd.Series, min_length: int = 20) -> pd.Series:
    """최소 길이 기준으로 텍스트를 필터링합니다."""
    return texts[texts.str.len() >= min_length]

def remove_duplicates(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    """중복된 텍스트를 제거합니다."""
    return df.drop_duplicates(subset=[text_column])

def get_stopwords() -> List[str]:
    """한국어 불용어 목록을 반환합니다."""
    stopwords = [
        # 일반적인 불용어
        '이', '그', '저', '것', '수', '등', '및', '또는', '그리고', '하지만', '그러나',
        '때문에', '위해서', '통해서', '의해서', '로서', '으로서', '에서', '에게서',
        '부터', '까지', '에서', '로', '으로', '에', '에게', '의', '가', '이', '은', '는',
        '을', '를', '도', '만', '도', '라도', '이라도', '이라도', '이라도',
        
        # 조사
        '이', '가', '을', '를', '은', '는', '도', '만', '부터', '까지', '에서', '로', '으로',
        '에', '에게', '의', '와', '과', '하고', '이랑', '랑', '나', '이나', '든지', '든가',
        '라도', '이라도', '이라도', '이라도', '이라도', '이라도', '이라도', '이라도',
        
        # 접속사
        '그리고', '또는', '하지만', '그러나', '그런데', '그래서', '따라서', '때문에',
        '위해서', '통해서', '의해서', '로서', '으로서', '에서', '에게서', '부터', '까지',
        
        # 대명사
        '나', '너', '우리', '저희', '그', '그녀', '그들', '이것', '그것', '저것', '무엇',
        '어떤', '어느', '몇', '얼마', '언제', '어디', '어떻게', '왜', '무엇을', '무엇이',
        
        # 부사
        '매우', '너무', '아주', '정말', '진짜', '완전', '전혀', '절대', '아무', '별로',
        '그냥', '그대로', '바로', '곧', '이미', '아직', '벌써', '갑자기', '갑작스럽게',
        
        # 형용사 (일반적인 것들)
        '좋은', '나쁜', '큰', '작은', '많은', '적은', '새로운', '오래된', '빠른', '느린',
        '높은', '낮은', '긴', '짧은', '넓은', '좁은', '무거운', '가벼운', '따뜻한', '차가운',
        
        # 동사 (일반적인 것들)
        '있다', '없다', '하다', '되다', '가다', '오다', '보다', '듣다', '말하다', '생각하다',
        '알다', '모르다', '원하다', '필요하다', '가능하다', '불가능하다', '좋다', '나쁘다',
        
        # 숫자 관련
        '하나', '둘', '셋', '넷', '다섯', '여섯', '일곱', '여덟', '아홉', '열',
        '첫째', '둘째', '셋째', '넷째', '다섯째',
        
        # 시간 관련
        '오늘', '어제', '내일', '지금', '이제', '언제', '언젠가', '아직', '벌써', '이미',
        
        # 장소 관련
        '여기', '저기', '거기', '어디', '어디든', '어디나', '어디서', '어디로', '어디에',
        
        # 기타 일반적인 단어들
        '문제', '사항', '내용', '관련', '대해', '통해', '의해', '위해', '때문', '이유',
        '결과', '원인', '방법', '방안', '해결', '개선', '확인', '검토', '검토', '검토',
        '문의', '상담', '요청', '신청', '제출', '접수', '처리', '완료', '진행', '중단',
        '취소', '변경', '수정', '삭제', '추가', '제거', '설치', '제거', '구매', '판매',
        '대여', '반납', '교환', '환불', '보증', '수리', '점검', '정비', '관리', '운영',
        '서비스', '지원', '도움', '협조', '협력', '협의', '합의', '동의', '반대', '찬성',
        '찬반', '논의', '토론', '회의', '회의', '회의', '회의', '회의', '회의', '회의',
        
        # 한 글자 단어들 (대부분 불용어)
        '가', '나', '다', '라', '마', '바', '사', '아', '자', '차', '카', '타', '파', '하',
        '각', '간', '갈', '감', '갑', '갓', '강', '개', '객', '거', '건', '걸', '검', '겁',
        '게', '격', '견', '결', '겸', '경', '계', '고', '곡', '곤', '곧', '골', '공', '과',
        '관', '광', '괴', '교', '구', '국', '군', '굴', '굳', '굴', '굽', '궁', '권', '궤',
        '귀', '규', '균', '그', '극', '근', '글', '금', '급', '긴', '길', '김', '깊', '까',
        '깨', '꼬', '꼭', '꼴', '꼼', '꼽', '꼿', '꽂', '꽃', '꽉', '꽤', '꾸', '꾼', '꿀',
        '꿈', '뀌', '끄', '끈', '끊', '끌', '끎', '끓', '끔', '끗', '끙', '끝', '끼', '끽',
        '낀', '나', '낙', '낚', '난', '날', '낡', '남', '납', '낫', '낭', '낮', '낯', '낱',
        '낳', '내', '냄', '냇', '냉', '냐', '냑', '냔', '냘', '냠', '냥', '너', '넉', '넋',
        '넌', '널', '넒', '넓', '넘', '넙', '넛', '넜', '넝', '넣', '네', '넥', '넨', '넬',
        '넴', '넵', '넷', '넸', '넹', '녀', '녁', '년', '녈', '념', '녑', '녔', '녕', '녘',
        '녜', '녠', '노', '녹', '논', '놀', '놂', '놈', '놉', '놋', '농', '높', '놓', '놔',
        '놘', '놜', '놨', '뇌', '뇐', '뇔', '뇜', '뇝', '뇟', '뇨', '뇩', '뇬', '뇰', '뇹',
        '뇻', '뇽', '누', '눅', '눈', '눋', '눌', '눔', '눕', '눗', '눙', '눠', '눴', '눼',
        '뉘', '뉜', '뉠', '뉨', '뉩', '뉴', '뉵', '뉼', '늄', '늅', '느', '늑', '는', '늘',
        '늙', '늚', '늠', '늡', '늣', '능', '늦', '늪', '늬', '늰', '늴', '니', '닉', '닌',
        '닐', '닒', '니', '닙', '닛', '닝', '닐', '닙', '닛', '닝', '닐', '닙', '닛', '닝',
        
        # 특정 도메인 불용어 (상담/게시판 관련)
        '문의', '상담', '요청', '신청', '제출', '접수', '처리', '완료', '진행', '중단',
        '취소', '변경', '수정', '삭제', '추가', '제거', '설치', '제거', '구매', '판매',
        '대여', '반납', '교환', '환불', '보증', '수리', '점검', '정비', '관리', '운영',
        '서비스', '지원', '도움', '협조', '협력', '협의', '합의', '동의', '반대', '찬성',
        '찬반', '논의', '토론', '회의', '회의', '회의', '회의', '회의', '회의', '회의',
        
        # 기타 일반적인 단어들
        '문제', '사항', '내용', '관련', '대해', '통해', '의해', '위해', '때문', '이유',
        '결과', '원인', '방법', '방안', '해결', '개선', '확인', '검토', '검토', '검토',
    ]
    
    return stopwords

def extract_ngrams(text: str, n: int = 2, min_freq: int = 2) -> List[Tuple[str, int]]:
    """N-gram을 추출합니다."""
    if pd.isna(text):
        return []
    
    # 텍스트 전처리
    text = str(text).strip()
    text = mask_personal_info(text)
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # 단어 분리
    words = text.split()
    
    # 불용어 제거
    stopwords = get_stopwords()
    words = [word for word in words if word not in stopwords and len(word) > 1]
    
    # N-gram 생성
    ngrams = []
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        ngrams.append(ngram)
    
    # 빈도 계산
    from collections import Counter
    ngram_counts = Counter(ngrams)
    
    # 최소 빈도 필터링
    filtered_ngrams = [(ngram, count) for ngram, count in ngram_counts.items() if count >= min_freq]
    
    # 빈도순 정렬
    filtered_ngrams.sort(key=lambda x: x[1], reverse=True)
    
    return filtered_ngrams

def analyze_ngrams(texts: List[str], n: int = 2, min_freq: int = 2) -> Dict[str, List[Tuple[str, int]]]:
    """여러 텍스트에서 N-gram을 분석합니다."""
    all_ngrams = []
    
    for text in texts:
        ngrams = extract_ngrams(text, n, min_freq)
        all_ngrams.extend(ngrams)
    
    # 전체 빈도 계산
    from collections import Counter
    total_counts = Counter()
    for ngram, count in all_ngrams:
        total_counts[ngram] += count
    
    # 최소 빈도 필터링
    filtered_ngrams = [(ngram, count) for ngram, count in total_counts.items() if count >= min_freq]
    filtered_ngrams.sort(key=lambda x: x[1], reverse=True)
    
    return {
        f'{n}-gram': filtered_ngrams
    }

def clean_text_for_wordcloud(text: str) -> str:
    """워드클라우드용 텍스트를 정리합니다."""
    if pd.isna(text):
        return ""
    
    # 기본 정리
    text = str(text).strip()
    
    # 개인정보 마스킹
    text = mask_personal_info(text)
    
    # 특수문자 제거 (한글, 영문, 숫자만 유지)
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 불용어 제거
    stopwords = get_stopwords()
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
    
    return ' '.join(filtered_words).strip() 