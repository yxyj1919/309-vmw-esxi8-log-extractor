"""
VMkernel Log 分类处理器

这个模块负责对过滤后的 VMkernel 日志进行分类处理。
主要功能：
1. 根据预定义的模块分类规则进行日志分类
2. 生成各类别的统计信息
3. 处理未匹配的日志记录

处理流程：
1. 加载模块分类定义
2. 对日志进行分类处理
3. 生成分类统计
4. 处理未匹配记录
"""

import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path

class VMK8LogRefiner:
    """
    VMkernel 日志分类处理器类
    
    主要职责：
    - 加载和管理模块分类规则
    - 根据规则对日志进行分类
    - 生成分类统计报告
    - 处理未匹配的记录
    
    属性：
    - module_categories: 模块分类规则字典
    """
    
    def __init__(self):
        """
        初始化分类处理器
        
        功能：
        1. 获取项目根目录
        2. 加载模块分类定义文件
        3. 初始化分类规则
        """
        try:
            # 获取项目根目录
            root_dir = Path(__file__).parent.parent.parent.parent
            json_path = os.path.join(root_dir, 'data', 'dicts', 'vmk_8_mod.json')
            
            # 加载模块分类定义
            with open(json_path, 'r', encoding='utf-8') as f:
                self.module_categories = json.load(f)
        except Exception as e:
            print(f"加载模块定义时发生错误: {str(e)}")
            self.module_categories = {}

    def process_dataframe(self, df):
        """
        处理数据框并按模块分类
        
        参数：
            df (pd.DataFrame): 输入数据框，需包含 Module 列
            
        返回：
            dict: 包含各分类的数据框的字典
        """
        if df is None or df.empty or 'Module' not in df.columns:
            print("输入数据为空或缺少 Module 列")
            return None

        # 初始化结果字典
        result = {
            'STORAGE': pd.DataFrame(),
            'NETWORK': pd.DataFrame(),
            'SYSTEM': pd.DataFrame(),
            'VSAN': pd.DataFrame(),
            'VM': pd.DataFrame(),
            'UNMATCHED': pd.DataFrame()
        }

        # 处理每个分类
        matched_mask = pd.Series(False, index=df.index)
        
        for category, modules in self.module_categories.items():
            # 使用更灵活的匹配逻辑
            mask = pd.Series(False, index=df.index)
            for module in modules:
                # 不区分大小写的匹配
                current_mask = df['Module'].str.contains(
                    module, 
                    case=False,  # 不区分大小写
                    regex=False, # 使用普通字符串匹配
                    na=False
                )
                mask = mask | current_mask
            
            result[category] = df[mask].copy()
            matched_mask = matched_mask | mask

        # 添加未匹配的记录
        result['UNMATCHED'] = df[~matched_mask].copy()

        # 调试模式下保存分类结果
        if os.getenv('VMK_DEBUG') == 'true':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存各类别结果
            for category, category_df in result.items():
                if not category_df.empty:
                    output_file = os.path.join(output_dir, 
                                             f'{timestamp}-vmk-3-refined-{category.lower()}.csv')
                    category_df.to_csv(output_file, index=False, encoding='utf-8')
                    print(f"调试模式：{category} 类别结果已保存到: {output_file}")

        return result

    def process_by_category(self, input_csv):
        """
        按类别处理CSV文件
        
        参数：
            input_csv (str): 输入CSV文件路径
            
        返回：
            dict: 包含各分类的数据框的字典
        """
        try:
            # 读取CSV文件
            df = pd.read_csv(input_csv)
            
            # 进行分类处理
            category_dfs = self.process_dataframe(df)
            
            # 处理未匹配的记录
            if category_dfs and 'UNMATCHED' in category_dfs:
                unmatched_df = category_dfs['UNMATCHED']
                if not unmatched_df.empty:
                    # 生成未匹配记录报告
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_dir = 'output'
                    unmatched_file = os.path.join(output_dir, 
                                                f'{timestamp}-vmk-3-refined-unmatched.csv')
                    
                    # 保存未匹配记录
                    unmatched_df.to_csv(unmatched_file, index=False, encoding='utf-8')
                    
                    # 打印统计信息
                    print(f"\n未匹配模块统计:")
                    print(f"找到 {len(unmatched_df)} 条未匹配记录")
                    print(f"已保存到: {unmatched_file}")
                    
                    # 显示未匹配的模块分布
                    print("\n未匹配模块分布:")
                    unmatched_modules = unmatched_df['Module'].value_counts()
                    for module, count in unmatched_modules.items():
                        print(f"  {module}: {count}条记录")

            return category_dfs
            
        except Exception as e:
            print(f"处理CSV文件时发生错误: {str(e)}")
            return {}

def main():
    """测试函数"""
    refiner = VMK8LogRefiner()
    
    # 假设我们要处理的CSV文件路径
    input_csv = "./output/20250130_173849-vmk-basic-filtered.csv"  # 替换为实际的CSV文件路径
    
    # 处理日志并获取所有类别的DataFrame
    category_dfs = refiner.process_by_category(input_csv)
    
    # 显示每个类别的DataFrame信息
    for category, df in category_dfs.items():
        if not df.empty:
            print(f"\n{category} DataFrame 信息:")
            print(f"记录数: {len(df)}")
            print("前5条记录:")
            print(df.head())

if __name__ == "__main__":
    main()
