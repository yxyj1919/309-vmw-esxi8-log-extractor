import pandas as pd
import re
from datetime import datetime
import os

class VMK8LogProcessor:
    """
    VMware内核日志处理器 - 基础版本
    功能：
    1. 处理三种类型的日志：vmkalert、vmkwarning、vmkernel
    2. 提取关键信息：时间戳、日志标签、日志级别、CPU信息、模块名等
    3. 支持多种日志格式的解析
    """
    def __init__(self):
        # === 基础正则表达式模式定义 ===
        
        # 1. 时间戳模式：支持两种格式
        # - 带毫秒格式：2025-01-20T01:44:25.919Z
        # - 不带毫秒格式：2025-01-23T22:10:20Z
        self.time_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z)'
        
        # 2. 日志标签模式：匹配2-3个字母后跟括号中的数字
        # 例如：Al(177), Wa(180), In(182)
        self.log_tag_pattern = r'([A-Za-z]{2,3}\(\d+\))'
        
        # 3. 日志级别模式：匹配三种可能的日志级别
        # - vmkalert: 警告级别
        # - vmkwarning: 警告级别
        # - vmkernel: 普通内核日志
        self.log_level_pattern = r'(vmkalert:|vmkwarning:|vmkernel:)'
        
        # === 组合模式：用于匹配完整的日志头部 ===
        self.basic_pattern = (
            f'^{self.time_pattern}'     # 从行首开始的时间戳
            r'\s+'                      # 空白字符分隔
            f'{self.log_tag_pattern}'   # 日志标签
            r'\s+'                      # 空白字符分隔
            f'{self.log_level_pattern}' # 日志级别
        )

        # === 过滤条件定义 ===
        # 允许处理的日志级别和标签类型
        self.allowed_levels = {'vmkalert:', 'vmkwarning:', 'vmkernel:'}
        self.allowed_tags = {'Al', 'Wa', 'In'}  # Al: Alert, Wa: Warning, In: Info

        # === 警告日志（vmkalert/vmkwarning）的特定模式 ===
        # CPU信息模式：匹配如 cpu66:2097709)
        self.cpu_pattern = r'cpu\d+:\d+\)'
        
        # 警告级别模式：匹配 ALERT: 或 WARNING:
        self.alarm_level_pattern = r'(ALERT:|WARNING:)'
        
        # 模块名模式：匹配冒号前的所有非冒号字符
        # 例如：<NMLX_ERR> 或 HBX:
        self.module_pattern = r'([^:]+):'

        # === vmkernel日志的特定模式 ===
        # 场景1：简单CPU信息后可能跟着模块名
        # 例如：cpu82:10238915)Deactivating 或 cpu106:2097709)NetqueueBal:
        self.vmkernel_cpu_module_pattern1 = r'(cpu\d+:\d+\))(?:([^:]+):)?'
        
        # 场景2：带opID的CPU信息后跟模块名
        # 例如：cpu63:2099984 opID=be121f44)SchedVsi:
        self.vmkernel_cpu_module_pattern2 = r'(cpu\d+:\d+\s+opID=[a-f0-9]+\))([^:]+):'

        # 添加更简单的模块提取模式
        self.simple_module_pattern = r'([^:]+):'

    def process_log_line(self, line):
        """
        处理单行日志，根据日志级别使用不同的处理方式
        
        参数:
            line (str): 待处理的日志行
            
        返回:
            dict: 包含解析后的各个字段，或None（如果不符合处理条件）
        """
        line_str = line.strip()
        
        # 初始化结果字典，包含所有可能的字段
        result = {
            'Time': '',           # 时间戳
            'LogTag': '',         # 日志标签
            'LogLevel': '',       # 日志级别
            'CPU': '',           # CPU信息
            'AlarmLevel': '',     # 警告级别（对于警告日志）
            'Module': '',         # 模块名
            'Log': '',           # 主要日志内容
            'CompleteLog': line_str  # 完整原始日志
        }
        
        # 匹配日志的基本部分（时间戳、标签、级别）
        match = re.match(self.basic_pattern, line_str)
        if match:
            time, log_tag, log_level = match.groups()
            result.update({
                'Time': time,
                'LogTag': log_tag,
                'LogLevel': log_level
            })
            
            # 获取剩余需要处理的内容
            remaining = line_str[match.end():].strip()
            
            # === 根据日志级别选择不同的处理方式 ===
            if log_level in ('vmkalert:', 'vmkwarning:'):
                # 处理警告类日志
                self._process_warning_log(remaining, result)
            else:
                # 处理普通vmkernel日志
                self._process_kernel_log(remaining, result)
            
            return result
        
        return None

    def _process_warning_log(self, remaining, result):
        """处理警告类日志的辅助方法"""
        # 1. 匹配CPU信息
        cpu_match = re.match(self.cpu_pattern, remaining)
        if cpu_match:
            result['CPU'] = cpu_match.group()
            remaining = remaining[cpu_match.end():].strip()
        
        # 2. 匹配警告级别
        alarm_match = re.search(self.alarm_level_pattern, remaining)
        if alarm_match:
            result['AlarmLevel'] = alarm_match.group(1)
            remaining = remaining[alarm_match.end():].strip()
        
        # 3. 匹配模块名
        module_match = re.match(self.module_pattern, remaining)
        if module_match:
            result['Module'] = module_match.group(1)
            remaining = remaining[module_match.end():].strip()
        
        # 4. 保存剩余内容为日志消息
        result['Log'] = remaining

    def _process_kernel_log(self, remaining, result):
        """处理普通内核日志的辅助方法"""
        # 先处理CPU信息
        cpu_match = re.match(r'cpu\d+:\d+(?:\s+opID=[a-f0-9]+)?\)', remaining)
        if cpu_match:
            result['CPU'] = cpu_match.group()
            remaining = remaining[cpu_match.end():].strip()
        
        # 尝试提取模块名（使用更简单的方式）
        module_match = re.match(self.simple_module_pattern, remaining)
        if module_match:
            result['Module'] = module_match.group(1)
            remaining = remaining[module_match.end():].strip()
        
        # 保存剩余内容为日志消息
        result['Log'] = remaining

    def process_log_file(self, filepath):
        """处理日志文件并返回DataFrame"""
        log_entries = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip():  # 跳过空行
                        entry = self.process_log_line(line)
                        if entry:  # 只添加非None的结果
                            log_entries.append(entry)
            
            # 创建DataFrame
            df = pd.DataFrame(log_entries)
            
            # 使用更灵活的时间解析
            if 'Time' in df.columns:
                df['Time'] = pd.to_datetime(
                    df['Time'],
                    format='mixed',
                    utc=True
                )
            
            # 只在调试模式下保存中间文件
            if os.getenv('VMK_DEBUG') == 'true':
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = 'output'
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f'{timestamp}-vmk-basic-1-processed.csv')
                df.to_csv(output_file, index=False, encoding='utf-8')
                print(f"调试模式：基础日志处理结果已保存到: {output_file}")
            
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