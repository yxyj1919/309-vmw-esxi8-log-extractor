import re
import pandas as pd
import os
from datetime import datetime

class VOBD8LogProcessor:
    """
    VMware ESXi vobd日志处理器类
    用于解析和处理vobd日志文件，将其转换为结构化的DataFrame格式
    """
    def __init__(self, upload_folder):
        """
        初始化日志处理器
        Args:
            upload_folder (str): 输出文件的保存目录
        """
        self.upload_folder = upload_folder

    def process_log_file(self, filepath):
        """处理日志文件并返回DataFrame"""
        try:
            print(f"正在处理日志文件: {filepath}")
            
            # 检查文件是否存在
            if not os.path.exists(filepath):
                print(f"错误: 文件不存在 - {filepath}")
                return None
                
            # 获取文件大小
            file_size = os.path.getsize(filepath)
            print(f"文件大小: {file_size} 字节")
            
            # 打开日志文件并逐行读取
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_lines = f.readlines()

            print(f"读取到 {len(raw_lines)} 行日志")
            if len(raw_lines) > 0:
                print("第一行日志示例:", raw_lines[0].strip())

            # 初始化存储解析后的行
            rows_list = []

            # 定义完整格式的正则表达式
            pattern_full = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\s+(\w+\(\d+\))\s+([^:]+):\s+\[([^\]]+)\]\s+(\d+us):\s+\[([^\]]+)\]\s+(.+)'
            # 定义简单格式的正则表达式
            pattern_simple = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z):\s+(.+)'

            for log_entry in raw_lines:
                log_entry = log_entry.strip()
                
                # 尝试匹配完整格式
                match_full = re.match(pattern_full, log_entry)
                if match_full:
                    time, log_level, other_1, correlator, other_2, module, log = match_full.groups()
                    rows_list.append({
                        "Time": time,
                        "Level": log_level,
                        "Other_1": other_1,
                        "Correlator": correlator,
                        "Other_2": other_2,
                        "Module": module,
                        "Log": log,
                        "CompleteLog": log_entry
                    })
                else:
                    # 尝试匹配简单格式
                    match_simple = re.match(pattern_simple, log_entry)
                    if match_simple:
                        time, log = match_simple.groups()
                        rows_list.append({
                            "Time": time,
                            "Level": "",
                            "Other_1": "",
                            "Correlator": "",
                            "Other_2": "",
                            "Module": "",
                            "Log": log,
                            "CompleteLog": log_entry
                        })
                    else:
                        # 如果两种格式都不匹配，将整行作为日志内容
                        rows_list.append({
                            "Time": "",
                            "Level": "",
                            "Other_1": "",
                            "Correlator": "",
                            "Other_2": "",
                            "Module": "",
                            "Log": log_entry,
                            "CompleteLog": log_entry
                        })

            df_logs = pd.DataFrame(rows_list)
            print(f"成功解析 {len(df_logs)} 行数据")

            # 在处理日志时添加调试信息
            if 'Module' in df_logs.columns:
                # 检查模块名中的特殊字符
                for module in df_logs['Module'].unique():
                    print(f"模块名: '{module}', 长度: {len(module)}")

            # 创建输出目录
            output_dir = os.path.join(self.upload_folder, 'output')
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f'{timestamp}_vobd_parsed.csv')
            
            # 保存处理后的日志到CSV文件
            df_logs.to_csv(output_file, index=False)
            print(f"原始解析结果已保存到: {output_file}")
            
            return df_logs

        except Exception as e:
            print(f"处理日志文件时出错: {str(e)}")
            return None