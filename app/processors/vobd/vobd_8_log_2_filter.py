import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from .vobd_8_log_1_processor import VOBD8LogProcessor

class VOBD8LogFilter:
    def __init__(self):
        """初始化过滤器，从JSON文件加载问题模块定义"""
        try:
            # 获取项目根目录
            root_dir = Path(__file__).parent.parent.parent.parent
            
            # 从data/dicts目录加载问题模块定义
            json_path = os.path.join(root_dir, 'data', 'dicts', 'vobd_8_problem_modules.json')
            
            with open(json_path, 'r', encoding='utf-8') as f:
                self.problem_modules = json.load(f)
                print(f"成功加载问题模块定义，包含 {len(self.problem_modules)} 个模块")
        except Exception as e:
            print(f"加载问题模块定义失败: {str(e)}")
            self.problem_modules = {}

    def filter_problems(self, df):
        """过滤包含问题的日志条目"""
        if not df.empty:
            # 清理模块名（去除前后空格，统一大小写）
            df['Module'] = df['Module'].str.strip().str.lower()
            problem_modules_keys = [k.strip().lower() for k in self.problem_modules.keys()]
            
            # 打印调试信息
            print("日志中的模块:", df['Module'].unique().tolist())
            print("定义的问题模块:", problem_modules_keys)
            
            # 匹配模块
            known_problems_mask = df['Module'].isin(problem_modules_keys)
            matched_df = df[known_problems_mask]
            
            # 打印匹配结果
            if not matched_df.empty:
                print("成功匹配的模块:", matched_df['Module'].unique().tolist())
            else:
                print("没有匹配到任何模块")
            
            return matched_df
        
        return df

    def get_unknown_problems(self, df):
        """
        获取包含problem关键词但不在已知问题模块列表中的日志
        Args:
            df: 输入的DataFrame
        Returns:
            DataFrame: 未知问题日志
        """
        if not df.empty:
            # 找出包含 'problem' 关键词的模块
            problem_modules_mask = df['Module'].str.contains('problem', case=False, na=False)
            # 在已知问题模块中的日志
            known_problems_mask = df['Module'].isin(self.problem_modules.keys())
            # 返回包含problem但不在已知列表中的日志
            return df[problem_modules_mask & ~known_problems_mask]
        return pd.DataFrame()