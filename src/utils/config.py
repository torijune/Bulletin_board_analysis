import yaml
import os
from pathlib import Path

def load_config(config_path="config.yaml"):
    """설정 파일을 로드합니다."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def get_output_path(config, filename):
    """출력 파일 경로를 생성합니다."""
    output_dir = Path(config['data']['output_dir'])
    return output_dir / filename

def ensure_output_dirs(config):
    """출력 디렉토리들을 생성합니다."""
    output_dir = Path(config['data']['output_dir'])
    dirs = [
        output_dir / 'csv',
        output_dir / 'reports',
        output_dir / 'visualizations' / 'wordclouds',
        output_dir / 'visualizations' / 'frequency_charts'
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return output_dir 