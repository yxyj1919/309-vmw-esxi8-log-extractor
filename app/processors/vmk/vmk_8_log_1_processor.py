"""
VMkernel Log 基础处理器

这个模块负责 VMkernel 日志的基础解析和处理。
主要功能：
1. 解析日志的基本组件（时间戳、标签、级别等）
2. 提取模块信息
3. 格式化日志内容

处理流程：
1. 使用正则表达式匹配日志组件
2. 提取并验证模块信息
3. 生成结构化的数据框
"""

import pandas as pd
import re
from datetime import datetime
import os

class VMK8LogProcessor:
    """
    VMkernel 日志处理器类
    
    主要职责：
    - 定义日志匹配的正则表达式
    - 解析单行日志内容
    - 处理整个日志文件
    - 生成结构化数据
    
    属性：
    - time_pattern: 时间戳匹配模式
    - log_tag_pattern: 日志标签匹配模式
    - log_level_pattern: 日志级别匹配模式
    - cpu_pattern: CPU信息匹配模式
    - module_pattern: 模块名匹配模式
    """
    
    def __init__(self):
        """初始化处理器，设置正则表达式模式"""
        # === 基础正则表达式模式定义 ===
        
        # 1. 时间戳模式：匹配 ISO 格式时间
        self.time_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z)'
        
        # 2. 日志标签模式：匹配所有可能的标签类型
        self.log_tag_pattern = r'([A-Za-z]{1,3}\(\d+\))'  # 匹配 In(182), Wa(180), Al(177) 等
        
        # 3. 日志级别模式：匹配所有可能的日志级别
        self.log_level_pattern = r'(vmkernel:|vmkwarning:|vmkalert:)'  # 确保所有级别都带冒号
        
        # 4. CPU信息模式：匹配 CPU 编号和操作 ID，包括可能的 WARNING/ALERT 标记
        self.cpu_pattern = r'cpu\d+:\d+\)(?:ALERT:\s*)?'  # 修改以包含 ALERT: 并捕获后面的空白
        
        # 5. 模块名模式：修改为更精确地匹配带标记的模块名和函数
        self.module_pattern = r'(?:(?:<[^>]+>\s+[^:\s]+)(?:(?:[^:]*?(?=:))|$))'

    def process_log_line(self, line):
        """
        处理单行日志
        
        参数：
            line (str): 待处理的日志行
            
        返回：
            dict: 包含解析后的各个字段，或None（如果不符合格式）
        """
        line_str = line.strip()
        
        # 初始化结果字典
        result = {
            'Time': '',           # 时间戳
            'LogTag': '',         # 日志标签
            'LogLevel': '',       # 日志级别
            'CPU': '',           # CPU信息
            'Module': '',         # 模块名
            'Log': '',           # 主要日志内容
            'CompleteLog': line_str  # 完整原始日志
        }
        
        # 匹配基本组件
        basic_pattern = (
            f'^{self.time_pattern}\\s+'    # 时间戳
            f'{self.log_tag_pattern}\\s+'  # 日志标签
            f'{self.log_level_pattern}'    # 日志级别
        )
        
        match = re.match(basic_pattern, line_str)
        if match:
            # 提取基本信息
            time, log_tag, log_level = match.groups()
            # 处理日志级别，移除可能的冒号
            log_level = log_level.rstrip(':')
            result.update({
                'Time': time,
                'LogTag': log_tag,
                'LogLevel': log_level
            })
            
            # 调试输出
            if os.getenv('VMK_DEBUG') == 'true':
                print(f"LogTag matched: {log_tag}")
                print(f"LogLevel matched: {log_level}")
            
            # 处理剩余部分
            remaining = line_str[match.end():].strip()
            self._process_remaining(remaining, result)
            
            return result
        
        return None

    def _process_remaining(self, remaining, result):
        """
        处理日志的剩余部分，根据日志级别使用不同的处理逻辑
        
        参数：
            remaining (str): 待处理的剩余文本
            result (dict): 当前的结果字典
        """
        # 匹配 CPU 信息
        cpu_match = re.match(self.cpu_pattern, remaining)
        if cpu_match:
            result['CPU'] = cpu_match.group()
            remaining = remaining[cpu_match.end():].strip()
            
            # 根据日志级别选择不同的处理逻辑
            if result['LogLevel'] in ['vmkwarning', 'vmkalert']:
                # vmkwarning 和 vmkalert 的处理逻辑
                # 直接查找尖括号标记和模块名
                module_match = re.match(r'(?:ALERT:\s*)?(<[^>]+>\s+[^:\s]+(?:(?:[^:]*?(?=:))|$))', remaining)
                if module_match:
                    result['Module'] = module_match.group(1).strip()
                    remaining = remaining[len(module_match.group(0)):].strip()
                    if remaining.startswith(':'):
                        remaining = remaining[1:].strip()
            else:
                # vmkernel 的处理逻辑
                # 直接匹配冒号前的内容作为模块名
                module_match = re.match(r'([^:]+):', remaining)
                if module_match:
                    result['Module'] = module_match.group(1).strip()
                    remaining = remaining[module_match.end():].strip()
        
        # 保存剩余内容为日志消息
        result['Log'] = remaining

    def process_log_file(self, filepath):
        """
        处理日志文件并返回DataFrame
        
        参数：
            filepath (str): 日志文件路径
            
        返回：
            pd.DataFrame: 处理后的数据框
        """
        try:
            log_entries = []
            
            # 读取并处理每一行
            with open(filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip():  # 跳过空行
                        entry = self.process_log_line(line)
                        if entry:  # 只添加有效的解析结果
                            log_entries.append(entry)
            
            # 创建DataFrame
            df = pd.DataFrame(log_entries)
            
            # 处理时间列
            if 'Time' in df.columns:
                df['Time'] = pd.to_datetime(
                    df['Time'],
                    format='mixed',  # 允许混合格式
                    utc=True        # 处理UTC时间
                )
            
            # 调试模式下保存中间文件
            if os.getenv('VMK_DEBUG') == 'true':
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = 'output'
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f'{timestamp}-vmk-1-processed.csv')
                df.to_csv(output_file, index=False, encoding='utf-8')
                print(f"调试模式：基础处理结果已保存到: {output_file}")
            
            return df
            
        except Exception as e:
            print(f"处理日志文件时发生错误: {str(e)}")
            return pd.DataFrame()

    def extract_module(self, log_text):
        """Extract module name from log text"""
        # 确保能识别 UNMAP6
        unmap_pattern = r'UNMAP\d*'
        match = re.search(unmap_pattern, log_text, re.IGNORECASE)
        if match:
            return match.group().upper()  # 返回大写形式
        
        # ... 其他模块提取逻辑