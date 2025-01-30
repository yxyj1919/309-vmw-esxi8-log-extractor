import streamlit as st
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from app.ui import vmk_view, vmkw_view, vobd_view

# 设置页面布局
st.set_page_config(
    page_title="VMware日志分析器",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """主界面：处理日志文件上传和类型选择"""
    
    st.title('VMware日志分析器')
    
    # 侧边栏：文件上传和类型选择
    st.sidebar.header('日志上传')
    
    # 日志类型选择
    log_type = st.sidebar.selectbox(
        '选择日志类型',
        ['VMKernel日志', 'VMKWarning日志', 'VOBD日志']
    )
    
    # 文件上传
    uploaded_file = st.sidebar.file_uploader(
        "上传日志文件",
        type=['log', 'txt']
    )
    
    if uploaded_file is not None:
        # 保存上传的文件
        logs_dir = 'logs'
        os.makedirs(logs_dir, exist_ok=True)
        file_path = os.path.join(logs_dir, uploaded_file.name)
        
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        st.sidebar.success(f'文件已上传: {uploaded_file.name}')
        
        # 根据日志类型调用相应的处理视图
        if log_type == 'VMKernel日志':
            vmk_view.show(file_path)
        elif log_type == 'VMKWarning日志':
            vmkw_view.show(file_path)
        else:  # VOBD日志
            vobd_view.show(file_path)
    else:
        st.info('请上传日志文件进行分析')

if __name__ == '__main__':
    main() 