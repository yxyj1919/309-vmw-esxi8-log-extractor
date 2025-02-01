import streamlit as st
import os
import sys
from pathlib import Path
import pandas as pd

# Add project root directory to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from app.ui import vmkw_view

st.set_page_config(page_title="vmkwarning Log", layout="wide")

def is_valid_vmkwarning_log(filename):
    """Check if it's a valid vmkwarning log file"""
    # Check if filename starts with vmkwarning
    if not filename.lower().startswith('vmkwarning'):
        return False
    
    # Check if file extension is .log or .all
    return filename.lower().endswith(('.log', '.all'))

# File upload
uploaded_file = st.sidebar.file_uploader(
    "Upload Log File",
    type=['log', 'all'],  # Allowed file extensions
    help="Please upload a vmkwarning log file (starting with 'vmkwarning', .log or .all format)"
)

if uploaded_file is not None:
    if is_valid_vmkwarning_log(uploaded_file.name):
        # Save uploaded file
        logs_dir = 'logs'
        os.makedirs(logs_dir, exist_ok=True)
        file_path = os.path.join(logs_dir, uploaded_file.name)
        
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        st.sidebar.success(f'File uploaded: {uploaded_file.name}')
        vmkw_view.show(file_path)
    else:
        st.error('Please upload a valid vmkwarning log file (must start with "vmkwarning" and end with .log or .all)')
else:
    st.info('Please upload a vmkwarning log file for analysis')

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