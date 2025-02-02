"""
VMKWarning Log Analysis Page

这个模块提供了 VMware ESXi 系统警告日志分析的页面界面。
主要功能：
1. 文件上传和验证
2. 调用 vmkw_view 进行警告日志分析和展示
3. 处理用户交互和错误情况

特点：
- 专注于系统警告信息的分析
- 支持按警告级别（WARNING/ALERT）过滤
- 提供警告信息的统计和趋势分析
"""

import streamlit as st
import sys
from pathlib import Path
import os
import pandas as pd

# 添加项目根目录到 Python 路径，确保可以导入其他模块
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from app.ui.vmkw_view import show

def main():
    """
    主函数：处理警告日志分析页面的逻辑
    
    流程：
    1. 设置页面标题
    2. 提供文件上传功能
    3. 验证上传的文件
    4. 调用分析和展示功能
    """
    
    # 设置页面标题
    st.title("vmkwarning Log Analysis")
    
    # 添加文件上传功能
    uploaded_file = st.file_uploader(
        "Upload vmkwarning log file",
        type=['log', 'all', 'txt'],  # 允许的文件类型
        help="Support formats: .log, .all, .txt"
    )
    
    if uploaded_file is not None:
        try:
            # 创建临时目录用于存储上传的文件
            logs_dir = 'logs'
            os.makedirs(logs_dir, exist_ok=True)
            
            # 生成临时文件路径
            file_path = os.path.join(logs_dir, uploaded_file.name)
            
            # 保存上传的文件
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # 在调试模式下设置环境变量
            if st.session_state.get('debug_mode', False):
                os.environ['VMK_DEBUG'] = 'true'
            else:
                os.environ['VMK_DEBUG'] = 'false'
            
            # 使用 vmkw_view.py 显示界面
            show(file_path)
            
        except Exception as e:
            # 错误处理和用户反馈
            st.error(f'Error processing file: {str(e)}')
            st.error('Please check if the file is a valid vmkwarning log file.')

def is_valid_vmkwarning_log(filename):
    """Check if it's a valid vmkwarning log file"""
    # Check if filename starts with vmkwarning
    if not filename.lower().startswith('vmkwarning'):
        return False
    
    # Check if file extension is .log or .all
    return filename.lower().endswith(('.log', '.all'))

def add_daily_stats(df):
    """Add daily statistics chart"""
    if 'Time' in df.columns:
        try:
            # 创建一个明确的副本
            df_stats = df.copy()
            # 在副本上进行操作
            df_stats['Time'] = pd.to_datetime(df_stats['Time'])
            df_stats['Date'] = df_stats['Time'].dt.date
            
            # 使用处理后的数据
            daily_counts = df_stats.groupby('Date').size().reset_index()
            daily_counts.columns = ['Date', 'Count']
            
            # 显示图表
            st.subheader('Daily Log Count Statistics')
            st.line_chart(daily_counts.set_index('Date'))
            
            # 显示详细数据
            st.subheader('Daily Statistics Details')
            st.dataframe(daily_counts, use_container_width=True, height=200)
        except Exception as e:
            st.error(f'Error processing time data: {str(e)}')

if __name__ == '__main__':
    main() 