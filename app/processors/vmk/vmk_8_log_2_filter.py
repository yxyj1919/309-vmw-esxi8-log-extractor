"""
VMkernel Log 过滤器

这个模块负责对基础处理后的 VMkernel 日志进行过滤。
主要功能：
1. 过滤出包含有效模块信息的日志
2. 支持自定义过滤条件
3. 生成过滤后的数据报告

处理流程：
1. 接收基础处理后的日志数据
2. 应用过滤条件
3. 生成过滤统计
4. 输出过滤后的结果
"""

import pandas as pd
from app.processors.vmk.vmk_8_log_1_processor import VMK8LogProcessor
import os
from datetime import datetime

class VMK8LogFilter:
    """
    VMkernel 日志过滤器类
    
    主要职责：
    - 过滤无效或不完整的日志记录
    - 提取和验证模块信息
    - 生成过滤统计报告
    - 保存过滤后的结果
    
    属性：
    - processor: 日志处理器实例
    - output_columns: 输出数据列配置
    """
    
    def __init__(self):
        """初始化过滤器，设置基本配置"""
        # 初始化日志处理器
        self.processor = VMK8LogProcessor()
        
        # 定义输出列及其顺序
        self.output_columns = [
            'Time',          # 时间戳
            'LogTag',        # 日志标签
            'LogLevel',      # 日志级别
            'CPU',          # CPU信息
            'Module',        # 模块名
            'Log',          # 主要日志内容
            'CompleteLog'    # 完整原始日志
        ]

    def filter_logs(self, input_file, output_file=None):
        """
        过滤日志文件，只保留包含模块信息的记录
        
        参数：
            input_file (str): 输入日志文件路径
            output_file (str, optional): 输出CSV文件路径
            
        返回：
            pd.DataFrame: 过滤后的数据框
        """
        try:
            # 处理日志文件
            df = self.processor.process_log_file(input_file)
            
            if df.empty:
                print("没有找到有效的日志记录")
                return df
            
            # 过滤出Module不为空的记录
            filtered_df = df[df['Module'].notna() & (df['Module'] != '')]
            
            # 重新排列列顺序
            filtered_df = filtered_df[self.output_columns]
            
            # 只在调试模式或明确指定输出文件时保存
            if output_file or os.getenv('VMK_DEBUG') == 'true':
                if not output_file:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_dir = 'output'
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f'{timestamp}-vmk-2-filtered.csv')
                
                filtered_df.to_csv(output_file, index=False, encoding='utf-8')
                print(f"过滤后的日志已保存到: {output_file}")
            
            # 打印统计信息
            print(f"\n过滤统计:")
            print(f"原始记录数: {len(df)}")
            print(f"过滤后记录数: {len(filtered_df)}")
            print(f"包含模块信息的记录比例: {len(filtered_df)/len(df)*100:.2f}%")
            
            # 显示模块分布
            if not filtered_df.empty:
                print("\n模块分布:")
                module_counts = filtered_df['Module'].value_counts()
                for module, count in module_counts.items():
                    print(f"  {module}: {count}条记录")
            
            return filtered_df
            
        except Exception as e:
            print(f"过滤日志时发生错误: {str(e)}")
            return pd.DataFrame()

    def filter_dataframe(self, df):
        """
        直接处理DataFrame而不是从文件读取
        
        参数：
            df (pd.DataFrame): 输入数据框
            
        返回：
            pd.DataFrame: 过滤后的数据框
        """
        try:
            if df.empty:
                return pd.DataFrame()
            
            # 过滤出Module不为空的记录
            filtered_df = df[df['Module'].notna() & (df['Module'] != '')]
            
            return filtered_df
            
        except Exception as e:
            print(f"过滤数据时发生错误: {str(e)}")
            return pd.DataFrame()

def main():
    """测试函数"""
    filter = VMK8LogFilter()
    
    # 测试文件路径
    test_file = "./logs/vmkernel-8-storage-ran.all"
    # 不指定输出文件，使用默认命名格式
    filtered_df = filter.filter_logs(test_file)
    
    if not filtered_df.empty:
        print("\n预览前5条过滤后的记录:")
        print(filtered_df.head())

if __name__ == "__main__":
    main()
