import json
import os
from ...app.processors.vobd.vobd_8_log_1_processor import VOBD8LogProcessor

class VOBD8LogFilter:
    def __init__(self):
        """初始化过滤器，从JSON文件加载问题模块定义"""
        try:
            # 从dicts目录加载问题模块定义
            json_path = os.path.join('dicts', 'vobd_problem_modules.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                self.problem_modules = json.load(f)
        except Exception as e:
            print(f"加载问题模块定义失败: {str(e)}")
            self.problem_modules = {}

    def filter_problems(self, df):
        """
        过滤包含问题的日志条目
        Args:
            df: 输入的DataFrame
        Returns:
            DataFrame: 过滤后的结果
        """
        if self.problem_modules and not df.empty:
            return df[df['Module'].isin(self.problem_modules.keys())]
        return df 