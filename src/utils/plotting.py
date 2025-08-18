import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import os

def setup_korean_font():
    """한글 폰트를 설정합니다."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # macOS에서 사용 가능한 한글 폰트들
        korean_fonts = [
            '/System/Library/Fonts/AppleGothic.ttf',
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc'
        ]
    elif system == "Windows":
        # Windows에서 사용 가능한 한글 폰트들
        korean_fonts = [
            'C:/Windows/Fonts/malgun.ttf',  # 맑은 고딕
            'C:/Windows/Fonts/gulim.ttc',   # 굴림
            'C:/Windows/Fonts/batang.ttc',  # 바탕
            'C:/Windows/Fonts/dotum.ttc'    # 돋움
        ]
    else:  # Linux
        # Linux에서 사용 가능한 한글 폰트들
        korean_fonts = [
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
        ]
    
    # 사용 가능한 폰트 찾기
    available_font = None
    for font_path in korean_fonts:
        if os.path.exists(font_path):
            available_font = font_path
            break
    
    if available_font:
        # 폰트 설정
        font_prop = fm.FontProperties(fname=available_font)
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
        print(f"한글 폰트 설정 완료: {available_font}")
        return True
    else:
        # 폰트를 찾을 수 없는 경우 기본 설정
        print("한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        return False

def get_korean_font_prop():
    """한글 폰트 속성을 반환합니다."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        font_paths = [
            '/System/Library/Fonts/AppleGothic.ttf',
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',
            '/System/Library/Fonts/PingFang.ttc'
        ]
    elif system == "Windows":
        font_paths = [
            'C:/Windows/Fonts/malgun.ttf',
            'C:/Windows/Fonts/gulim.ttc'
        ]
    else:  # Linux
        font_paths = [
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'
        ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            return fm.FontProperties(fname=font_path)
    
    # 폰트를 찾을 수 없는 경우 None 반환
    return None

def create_korean_plot(title="", xlabel="", ylabel="", figsize=(10, 6)):
    """한글 폰트가 적용된 플롯을 생성합니다."""
    # 한글 폰트 설정
    setup_korean_font()
    
    # 플롯 생성
    fig, ax = plt.subplots(figsize=figsize)
    
    # 제목과 라벨 설정
    if title:
        ax.set_title(title, fontsize=16, pad=20)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    
    return fig, ax 