# Move content from vmkw_8_log_processor.py
# Content remains the same 

import pandas as pd
import re
from datetime import datetime
import os

class VMKW8LogProcessor:
    """
    VMware kernel warning log processor
    For parsing and processing VMware ESXi system kernel warning logs
    """
    def __init__(self):
        # Define regex patterns for log components
        
        # Match ISO format timestamp, e.g.: 2025-01-19T19:12:20.060Z
        self.group1_time_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)'
        
        # Match log tag, format is letters followed by numbers in parentheses, e.g.: Wa(180)
        self.group2_log_tag_pattern = r'([A-Za-z]+\(\d+\))'
        
        # Match log level ending with colon, e.g.: vmkwarning:
        self.group3_log_level_pattern = r'([a-z]+:)'
        
        # Match CPU info, format is cpuX:Y, e.g.: cpu32:2098009
        self.group4_cpu_pattern = r'(cpu\d+:\d+)'
        
        # Match alarm level, uppercase letters followed by colon, e.g.: WARNING:
        self.group5_alarm_level_pattern = r'([A-Z]+):'
        
        # Match log message content to end of line
        self.group7_log_pattern = r'(.+)$'
        
        # Combine all patterns into complete log matching regex
        self.log_pattern = (
            f'^{self.group1_time_pattern}\\s+'  # Start with timestamp
            f'{self.group2_log_tag_pattern}\\s+'  # Followed by log tag
            f'{self.group3_log_level_pattern}\\s+'  # Log level
            f'({self.group4_cpu_pattern})\\s*'  # CPU info
            f'({self.group5_alarm_level_pattern})\\s*'  # Alarm level
            f'([^:]+):\\s*'  # Module name (non-colon chars until colon)
            f'({self.group7_log_pattern})$'  # Log content until end of line
        )
        
    def process_log_line(self, line):
        """
        Process single line of log content
        
        Args:
            line (str): Log line to process
            
        Returns:
            dict: Dictionary containing parsed log components
        """
        line_str = line.strip()  # Remove leading/trailing whitespace
        # Initialize result dictionary with default values
        result = {
            'Time': '',
            'LogTag': '',
            'LogLevel': '',
            'CPU': '',
            'AlarmLevel': '',                
            'Module': '',
            'Log': line_str,
            'CompleteLog': line_str  # Save complete original log
        }
        
        # Try to match log line with complete pattern
        match = re.match(self.log_pattern, line_str)
        
        if match:
            # If full match successful, extract all components
            time, log_tag, log_level, cpu, alarm_level, module, log = match.groups()
            # Process module name, set to empty string if 'unknown'
            module_value = module.strip() if module and module.strip() != 'unknown' else ''
            return {
                'Time': time,
                'LogTag': log_tag,
                'LogLevel': log_level,
                'CPU': cpu,
                'AlarmLevel': alarm_level,
                'Module': module_value,
                'Log': log.strip(),
                'CompleteLog': line_str
            }
        else:
            # If full match fails, try to match components individually
            # First match timestamp
            time_match = re.match(self.group1_time_pattern, line_str)
            if time_match:
                result['Time'] = time_match.group(1)
                # Get remaining content after timestamp
                remaining = line_str[len(time_match.group(1)):].strip()
                
                # Match other components sequentially
                log_tag_match = re.search(self.group2_log_tag_pattern, remaining)
                if log_tag_match:
                    result['LogTag'] = log_tag_match.group(1)
                
                log_level_match = re.search(self.group3_log_level_pattern, remaining)
                if log_level_match:
                    result['LogLevel'] = log_level_match.group(1)

                cpu_match = re.search(self.group4_cpu_pattern, remaining)
                if cpu_match:
                    result['CPU'] = cpu_match.group(1)

                alarm_level_match = re.search(self.group5_alarm_level_pattern, remaining)
                if alarm_level_match:
                    result['AlarmLevel'] = alarm_level_match.group(1)                    
                
                # Extract module name (content between alarm level and first colon)
                if alarm_level_match:
                    alarm_level_index = remaining.find(alarm_level_match.group(1) + ':')
                    if alarm_level_index != -1:
                        remaining_after_alarm = remaining[alarm_level_index + len(alarm_level_match.group(1)) + 1:].strip()
                        module_match = re.match(r'([^:]+):', remaining_after_alarm)
                        if module_match:
                            result['Module'] = module_match.group(1).strip()
                            result['Log'] = remaining_after_alarm[len(module_match.group(0)):].strip()
                
        return result

    def process_log_file(self, filepath):
        """处理日志文件并返回DataFrame"""
        try:
            log_entries = []
            
            with open(filepath, 'r', encoding='utf-8') as log_file:
                for line in log_file:
                    if line.strip():  # Skip empty lines
                        log_entry = self.process_log_line(line)
                        if log_entry:  # Ensure valid log entry
                            log_entries.append(log_entry)
            
            # Return empty DataFrame if no valid log entries
            if not log_entries:
                print("Warning: No valid log entries found")
                return pd.DataFrame(columns=['Time', 'LogTag', 'LogLevel', 'CPU', 
                                          'AlarmLevel', 'Module', 'Log', 'CompleteLog'])
            
            # Create DataFrame
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
                output_file = os.path.join(output_dir, f'{timestamp}-vmkw-1-processed.csv')
                df.to_csv(output_file, index=False, encoding='utf-8')
                print(f"调试模式：基础日志处理结果已保存到: {output_file}")
            
            return df
            
        except Exception as e:
            print(f"处理日志文件时发生错误: {str(e)}")
            return pd.DataFrame()

    def _process_warning_log(self, remaining, result):
        """处理警告类日志的辅助方法"""
        # 1. 匹配CPU信息
        cpu_match = re.match(self.group4_cpu_pattern, remaining)
        if cpu_match:
            result['CPU'] = cpu_match.group(1)
            remaining = remaining[cpu_match.end():].strip()
        
        # 2. 匹配警告级别
        alarm_match = re.search(self.group5_alarm_level_pattern, remaining)
        if alarm_match:
            result['AlarmLevel'] = alarm_match.group(1)
            remaining = remaining[alarm_match.end():].strip()
        
        # 3. 匹配模块名 - 这里直接从冒号前提取
        module_match = re.match(r'([^:]+):', remaining)
        if module_match:
            result['Module'] = module_match.group(1)
            remaining = remaining[module_match.end():].strip()
        
        # 4. 匹配日志内容
        result['Log'] = remaining.strip()
        result['CompleteLog'] = remaining.strip()
        
        return result 