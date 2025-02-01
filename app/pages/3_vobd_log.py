"""
VOBD Log Analysis Page

这个模块提供了 VMware ESXi vobd (VMkernel Observation) 日志分析的页面界面。
主要功能：
1. 文件上传和验证
2. 调用 vobd_view 进行系统诊断日志分析和展示
3. 处理用户交互和错误情况

特点：
- 专注于系统诊断和观察信息
- 支持启动和运行时的系统状态分析
- 提供系统问题的诊断和统计
"""

import streamlit as st
import sys
from pathlib import Path
import os

# 添加项目根目录到 Python 路径，确保可以导入其他模块
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from app.ui.vobd_view import show

def main():
    """
    主函数：处理 vobd 日志分析页面的逻辑
    
    流程：
    1. 设置页面标题
    2. 提供文件上传功能
    3. 验证上传的文件
    4. 调用分析和展示功能
    
    特点：
    - 支持多种日志文件格式
    - 提供文件格式验证
    - 包含错误处理和用户反馈
    - 专注于系统诊断信息
    """
    
    # 设置页面标题
    st.title("vobd Log Analysis")
    
    # 添加文件上传功能
    uploaded_file = st.file_uploader(
        "Upload vobd log file",
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
            
            # 调用视图模块展示分析结果
            show(file_path)
            
        except Exception as e:
            # 错误处理和用户反馈
            st.error(f'Error processing file: {str(e)}')
            st.error('Please check if the file is a valid vobd log file.')

if __name__ == '__main__':
    main() 