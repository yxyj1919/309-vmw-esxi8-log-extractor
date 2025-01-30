import pandas as pd
import re
from datetime import datetime
import os

class VMKW8LogProcessor:
    """
    VMware内核警告日志处理器
    用于解析和处理VMware ESXi系统的内核警告日志
    """
    def __init__(self):
        # 使用正则表达式定义各个日志组件的匹配模式
        
        # 匹配ISO格式的时间戳，例如：2025-01-19T19:12:20.060Z
        self.group1_time_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)'
        
        # 匹配日志标签，格式为字母后跟括号中的数字，例如：Wa(180)
        self.group2_log_tag_pattern = r'([A-Za-z]+\(\d+\))'
        
        # 匹配日志级别，以冒号结尾，例如：vmkwarning:
        self.group3_log_level_pattern = r'([a-z]+:)'
        
        # 匹配CPU信息，格式为cpuX:Y，例如：cpu32:2098009
        self.group4_cpu_pattern = r'(cpu\d+:\d+)'
        
        # 匹配报警级别，全大写字母后跟冒号，例如：WARNING:
        self.group5_alarm_level_pattern = r'([A-Z]+):'
        
        # 匹配日志消息内容，匹配到行尾的所有内容
        self.group7_log_pattern = r'(.+)$'
        
        # 组合所有模式成为完整的日志匹配正则表达式
        # 使用f-string将所有模式组合，并添加适当的空白符
        self.log_pattern = (
            f'^{self.group1_time_pattern}\\s+'  # 以时间戳开始
            f'{self.group2_log_tag_pattern}\\s+'  # 后跟日志标签
            f'{self.group3_log_level_pattern}\\s+'  # 日志级别
            f'({self.group4_cpu_pattern})\\s*'  # CPU信息
            f'({self.group5_alarm_level_pattern})\\s*'  # 报警级别
            f'([^:]+):\\s*'  # 模块名（到冒号为止的非冒号字符）
            f'({self.group7_log_pattern})$'  # 日志具体内容直到行尾
        )
        
    def process_log_line(self, line):
        """
        处理单行日志内容
        
        参数:
            line (str): 需要处理的日志行
            
        返回:
            dict: 包含解析后的各个日志组件的字典
        """
        line_str = line.strip()  # 去除首尾空白字符
        # 初始化结果字典，设置默认值
        result = {
            'Time': '',
            'LogTag': '',
            'LogLevel': '',
            'CPU': '',
            'AlarmLevel': '',                
            'Module': '',
            'Log': line_str,
            'CompleteLog': line_str  # 保存完整的原始日志
        }
        
        # 尝试用完整模式匹配日志行
        match = re.match(self.log_pattern, line_str)
        
        if match:
            # 如果完全匹配成功，提取所有组件
            time, log_tag, log_level, cpu, alarm_level, module, log = match.groups()
            # 处理模块名，如果是'unknown'则设为空字符串
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
            # 如果完整匹配失败，尝试逐个匹配各个组件
            # 首先匹配时间戳
            time_match = re.match(self.group1_time_pattern, line_str)
            if time_match:
                result['Time'] = time_match.group(1)
                # 获取时间戳之后的剩余内容
                remaining = line_str[len(time_match.group(1)):].strip()
                
                # 依次匹配其他组件
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
                
                # 提取模块名（在报警级别之后，第一个冒号之前的内容）
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
        """
        处理日志文件并返回DataFrame
        
        参数:
            filepath (str): 日志文件的路径
            
        返回:
            pd.DataFrame: 包含处理后日志数据的DataFrame
        """
        log_entries = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as log_file:  # 改用更明确的变量名
                for line in log_file:
                    if line.strip():  # 跳过空行
                        log_entry = self.process_log_line(line)
                        if log_entry:  # 确保返回了有效的日志条目
                            log_entries.append(log_entry)
            
            # 如果没有有效的日志条目，返回空DataFrame
            if not log_entries:
                print("警告：未找到有效的日志条目")
                return pd.DataFrame(columns=['Time', 'LogTag', 'LogLevel', 'CPU', 
                                          'AlarmLevel', 'Module', 'Log', 'CompleteLog'])
            
            # 创建DataFrame
            df = pd.DataFrame(log_entries)
            
            # 确保所有必需的列都存在
            required_columns = ['Time', 'LogTag', 'LogLevel', 'CPU', 
                              'AlarmLevel', 'Module', 'Log', 'CompleteLog']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # 按照指定顺序排列列
            df = df[required_columns]
            
            # 生成输出文件名和路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)
            
            # 构建输出文件路径
            output_file = os.path.join(output_dir, f'{timestamp}-vmkw-1-processed.csv')
            
            # 保存为CSV文件
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"日志已成功保存到: {output_file}")
            
            return df
            
        except Exception as e:
            print(f"处理日志文件时发生错误: {str(e)}")
            return pd.DataFrame(columns=['Time', 'LogTag', 'LogLevel', 'CPU', 
                                       'AlarmLevel', 'Module', 'Log', 'CompleteLog'])
