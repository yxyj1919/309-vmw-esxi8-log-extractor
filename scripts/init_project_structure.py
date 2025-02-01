import os
from pathlib import Path

def create_project_structure():
    """创建项目目录结构"""
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent
    
    # 定义需要创建的目录结构
    directories = [
        'app/pages',
        'app/processors/vmk',
        'app/processors/vmkw',
        'app/processors/vobd',
        'app/ui',
        'data/dicts/backups',
        'data/dicts/exports',
        'data/dicts/imports',
        'debug',
        'logs/output',
        'logs/unknown_problems',
        'scripts'
    ]
    
    # 创建目录
    for dir_path in directories:
        full_path = os.path.join(root_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"创建目录: {full_path}")
    
    # 创建 .gitkeep 文件以保持空目录
    empty_dirs = [
        'data/dicts/backups',
        'data/dicts/exports',
        'data/dicts/imports',
        'logs/output',
        'logs/unknown_problems'
    ]
    
    for dir_path in empty_dirs:
        gitkeep_path = os.path.join(root_dir, dir_path, '.gitkeep')
        with open(gitkeep_path, 'w') as f:
            pass
        print(f"创建文件: {gitkeep_path}")

if __name__ == '__main__':
    create_project_structure() 