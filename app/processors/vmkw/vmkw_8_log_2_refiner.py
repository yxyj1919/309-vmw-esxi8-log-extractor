# Move content from vmkw_8_log_refiner.py
# Content remains the same 

import json
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

class VMKW8LogRefiner:
    """VMKWarning log refiner for categorizing logs by module"""
    
    def __init__(self):
        """Initialize refiner with module definitions"""
        try:
            # Get project root directory
            root_dir = Path(__file__).parent.parent.parent.parent
            json_path = os.path.join(root_dir, 'data', 'dicts', 'vmk_8_mod.json')
            
            # Load module definitions
            with open(json_path, 'r', encoding='utf-8') as f:
                self.module_categories = json.load(f)
        except Exception as e:
            print(f"Error loading module definitions: {str(e)}")
            self.module_categories = {}

    def process_dataframe(self, df):
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