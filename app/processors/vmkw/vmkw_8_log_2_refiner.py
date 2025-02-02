# Move content from vmkw_8_log_refiner.py
# Content remains the same 

import json
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from app.processors.vmk.vmk_8_modules_manager import VMKModulesManager

class VMKW8LogRefiner:
    """VMKWarning 日志分类处理器"""
    
    def __init__(self):
        """初始化分类处理器"""
        # 加载模块定义
        manager = VMKModulesManager()
        self.module_categories = manager.get_all_modules()

    def process_dataframe(self, df):
        """处理数据框并按模块分类"""
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

        try:
            # 调试输出：显示所有待分类的模块
            if os.getenv('VMK_DEBUG') == 'true':
                print("\n=== 待分类的模块 ===")
                print(df['Module'].unique())
                print("\n=== 模块定义 ===")
                for cat, mods in self.module_categories.items():
                    print(f"\n{cat}:")
                    print(mods)

            # 处理每个分类
            matched_mask = pd.Series(False, index=df.index)
            
            for category, modules in self.module_categories.items():
                mask = pd.Series(False, index=df.index)
                for module in modules:
                    # 使用 contains 匹配，因为模块名可能是部分匹配
                    current_mask = df['Module'].str.contains(
                        module,
                        case=True,  # 保持大小写敏感
                        regex=False, # 使用普通字符串匹配
                        na=False    # 处理空值
                    )
                    
                    # 调试输出：显示每次匹配的结果
                    if os.getenv('VMK_DEBUG') == 'true' and current_mask.any():
                        print(f"\n=== 匹配模块: {module} -> {category} ===")
                        matched_modules = df[current_mask]['Module'].unique()
                        print(f"匹配到的模块: {matched_modules}")
                        print(f"匹配到的记录数: {current_mask.sum()}")
                    
                    mask = mask | current_mask
                
                result[category] = df[mask].copy()
                matched_mask = matched_mask | mask

            # 添加未匹配的记录
            result['UNMATCHED'] = df[~matched_mask].copy()
            
            # 调试输出：显示分类结果
            if os.getenv('VMK_DEBUG') == 'true':
                print("\n=== 分类结果 ===")
                for category, category_df in result.items():
                    if not category_df.empty:
                        print(f"\n{category} 类别:")
                        print(f"记录数: {len(category_df)}")
                        print("模块列表:")
                        print(category_df['Module'].unique())

            return result
            
        except Exception as e:
            print(f"处理数据时发生错误: {str(e)}")
            return None

    def process_dataframe_old(self, df):
        """
        Process DataFrame and categorize logs by module
        
        Args:
            df (pd.DataFrame): Input DataFrame with Module column
            
        Returns:
            dict: Dictionary of categorized DataFrames
        """
        if df is None or df.empty or 'Module' not in df.columns:
            return None

        result = {
            'STORAGE': pd.DataFrame(),
            'NETWORK': pd.DataFrame(),
            'SYSTEM': pd.DataFrame(),
            'VSAN': pd.DataFrame(),
            'VM': pd.DataFrame(),
            'UNMATCHED': pd.DataFrame()
        }

        # Process each category
        for category, modules in self.module_categories.items():
            mask = df['Module'].isin(modules)
            result[category] = df[mask].copy()
            # Remove matched rows from df to prevent duplicate matching
            df = df[~mask]

        # Add remaining unmatched logs to UNMATCHED category
        if not df.empty:
            result['UNMATCHED'] = df

        # 只在调试模式下保存分类结果
        if os.getenv('VMK_DEBUG') == 'true':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存分类结果
            for category, category_df in result.items():
                if not category_df.empty:
                    output_file = os.path.join(output_dir, 
                                             f'{timestamp}-vmkw-2-refined-{category.lower()}.csv')
                    category_df.to_csv(output_file, index=False, encoding='utf-8')
                    print(f"调试模式：{category} 类别结果已保存到: {output_file}")

        return result 