import pandas as pd
import json
import os
from datetime import datetime

class VMK8LogRefiner:
    """
    VMware内核日志细化处理器
    功能：
    1. 读取CSV文件到DataFrame
    2. 根据模块类别进行分类
    3. 生成分类后的CSV报告
    """
    def __init__(self):
        # 加载模块分类字典
        self.module_categories = self._load_module_dict()
        
    def _load_module_dict(self):
        """加载模块分类字典"""
        try:
            # 使用相对于项目根目录的路径
            dict_path = os.path.join(os.path.dirname(__file__), '../../../data/dicts/vmk_8_mod.json')
            with open(dict_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载模块字典时发生错误: {str(e)}")
            return {}

    def process_by_category(self, input_csv):
        """
        按类别处理日志
        
        参数:
            input_csv (str): 输入CSV文件路径
            
        返回:
            dict: 包含所有类别DataFrame的字典，包括未匹配的记录
                 格式: {'STORAGE': df_storage, 'NETWORK': df_network, ..., 'UNMATCHED': df_unmatched}
        """
        try:
            # 读取CSV文件
            df = pd.read_csv(input_csv)
            print(f"成功读取CSV文件，共 {len(df)} 条记录")
            
            # 创建一个字典来存储所有类别的DataFrame
            category_dfs = {}
            
            # 创建一个标记数组，用于跟踪已匹配的记录
            matched_mask = pd.Series(False, index=df.index)
            
            # 为每个类别创建过滤后的DataFrame
            for category, modules in self.module_categories.items():
                # 创建一个空的过滤条件
                mask = pd.Series(False, index=df.index)
                
                # 对每个模块名进行匹配
                for module in modules:
                    # 使用字符串包含操作而不是精确匹配
                    mask = mask | df['Module'].str.contains(module, regex=False, na=False)
                
                # 更新已匹配记录的标记
                matched_mask = matched_mask | mask
                
                # 使用组合的过滤条件
                filtered_df = df[mask]
                
                # 保存该类别的DataFrame
                category_dfs[category] = filtered_df
                
                if not filtered_df.empty:
                    # 生成输出文件名
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_dir = 'output'
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, 
                                             f'{timestamp}-vmk-basic-3-refined-{category.lower()}.csv')
                    
                    # 保存过滤后的结果
                    filtered_df.to_csv(output_file, index=False, encoding='utf-8')
                    
                    # 打印统计信息
                    print(f"\n{category} 类别统计:")
                    print(f"找到 {len(filtered_df)} 条记录")
                    print(f"已保存到: {output_file}")
                    
                    # 显示该类别中的模块分布
                    print("\n模块分布:")
                    module_counts = filtered_df['Module'].value_counts()
                    for module, count in module_counts.items():
                        print(f"  {module}: {count}条记录")
                else:
                    print(f"\n{category} 类别: 未找到匹配记录")

            # 处理未匹配的记录
            unmatched_df = df[~matched_mask]
            # 将未匹配记录添加到返回字典中
            category_dfs['UNMATCHED'] = unmatched_df
            
            if not unmatched_df.empty:
                # 生成未匹配记录的输出文件
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = 'output'
                unmatched_file = os.path.join(output_dir, 
                                            f'{timestamp}-vmk-basic-3-refined-unmatched.csv')
                
                # 保存未匹配的记录
                unmatched_df.to_csv(unmatched_file, index=False, encoding='utf-8')
                
                # 打印未匹配记录的统计信息
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

    def process_dataframe(self, df):
        """直接处理DataFrame而不是从文件读取"""
        try:
            if df.empty:
                return {}
            
            category_dfs = {}
            # 为每个类别创建过滤后的DataFrame
            for category, modules in self.module_categories.items():
                # 创建一个空的过滤条件
                mask = pd.Series(False, index=df.index)
                
                # 对每个模块名进行匹配
                for module in modules:
                    # 使用字符串包含操作而不是精确匹配
                    mask = mask | df['Module'].str.contains(module, regex=False, na=False)
                
                # 使用组合的过滤条件
                filtered_df = df[mask]
                category_dfs[category] = filtered_df
                
            # 添加未匹配的记录
            matched_mask = pd.Series(False, index=df.index)
            for category_df in category_dfs.values():
                if not category_df.empty:
                    matched_mask = matched_mask | df.index.isin(category_df.index)
            
            category_dfs['UNMATCHED'] = df[~matched_mask]
            
            return category_dfs
            
        except Exception as e:
            print(f"处理数据时发生错误: {str(e)}")
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
