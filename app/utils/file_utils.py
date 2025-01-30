import os
import pandas as pd
from datetime import datetime

def ensure_dir(dir_path):
    """确保目录存在，如果不存在则创建"""
    os.makedirs(dir_path, exist_ok=True)

def generate_output_path(base_dir, prefix, suffix):
    """生成输出文件路径
    
    参数:
        base_dir (str): 基础目录
        prefix (str): 文件前缀
        suffix (str): 文件后缀
    """
    ensure_dir(base_dir)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(base_dir, f'{timestamp}-{prefix}-{suffix}.csv')

def save_dataframe(df, file_path):
    """保存DataFrame到CSV文件"""
    df.to_csv(file_path, index=False, encoding='utf-8')
    return file_path 