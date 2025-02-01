import streamlit as st
import pandas as pd
import os
from app.processors.vmk.vmk_8_log_1_processor import VMK8LogProcessor
from app.processors.vmk.vmk_8_log_2_filter import VMK8LogFilter
from app.processors.vmk.vmk_8_log_3_refine import VMK8LogRefiner

# 设置页面布局为宽屏模式
st.set_page_config(
    page_title="VMware内核日志分析器",
    page_icon="📊",
    layout="wide",  # 使用宽屏布局
    initial_sidebar_state="expanded"
)

def load_latest_csv(pattern):
    """
    加载最新的CSV文件
    
    参数:
        pattern (str): 文件名模式，例如 'vmk-basic-1-processed'
        
    返回:
        pd.DataFrame: 加载的数据框
    """
    output_dir = 'output'
    if not os.path.exists(output_dir):
        return None
        
    # 查找匹配的文件
    matching_files = [f for f in os.listdir(output_dir) if pattern in f]
    if not matching_files:
        return None
        
    # 获取最新的文件
    latest_file = sorted(matching_files)[-1]
    file_path = os.path.join(output_dir, latest_file)
    
    return pd.read_csv(file_path)

def add_daily_stats(df):
    """添加每日统计图表
    
    参数:
        df: 包含Time列的DataFrame
    """
    if 'Time' in df.columns:
        try:
            # 使用ISO格式解析时间
            df['Time'] = pd.to_datetime(df['Time'], format='ISO8601')
            # 提取日期部分
            df['Date'] = df['Time'].dt.date
            # 按日期统计
            daily_counts = df.groupby('Date').size().reset_index()
            daily_counts.columns = ['Date', 'Count']
            
            # 显示每日统计图表
            st.subheader('每日日志数量统计')
            
            # 创建折线图
            st.line_chart(
                daily_counts.set_index('Date')
            )
            
            # 显示具体数据
            st.subheader('每日统计详情')
            st.dataframe(
                daily_counts,
                use_container_width=True,
                height=200
            )
        except Exception as e:
            st.error(f'处理时间数据时出错: {str(e)}')

def main():
    """主函数：使用Streamlit展示VMware内核日志分析结果"""
    
    st.title('VMware内核日志分析器')
    
    # 侧边栏：文件选择
    st.sidebar.header('数据选择')
    data_type = st.sidebar.selectbox(
        '选择数据类型',
        ['原始处理', '过滤后', '按类别细化']
    )
    
    # 检查是否有数据文件
    df = None
    
    if data_type == '原始处理':
        df = load_latest_csv('vmk-basic-1-processed')
        if df is not None:
            st.header('原始处理数据')
            st.write(f'总记录数: {len(df)}')
            
            # 数据过滤选项
            st.subheader('过滤选项')
            col1, col2 = st.columns(2)
            with col1:
                selected_level = st.multiselect(
                    '日志级别',
                    df['LogLevel'].unique().tolist()
                )
            with col2:
                selected_tag = st.multiselect(
                    '日志标签',
                    df['LogTag'].unique().tolist()
                )
            
            # 应用过滤
            if selected_level:
                df = df[df['LogLevel'].isin(selected_level)]
            if selected_tag:
                df = df[df['LogTag'].isin(selected_tag)]
            
            # 显示数据
            st.subheader('日志数据')
            # 使用 use_container_width=True 让表格占满容器宽度
            # height 参数设置表格高度（像素）
            st.dataframe(
                df,
                use_container_width=True,  # 使用容器宽度
                height=600  # 设置表格高度为600像素
            )
            
            # 显示统计信息
            st.subheader('统计信息')
            col1, col2 = st.columns(2)
            with col1:
                st.write('日志级别分布')
                st.write(df['LogLevel'].value_counts())
            with col2:
                st.write('日志标签分布')
                st.write(df['LogTag'].value_counts())
            
            # 添加每日统计
            add_daily_stats(df)
                
    elif data_type == '过滤后':
        df = load_latest_csv('vmk-basic-2-filtered')
        if df is not None:
            st.header('过滤后数据')
            st.write(f'总记录数: {len(df)}')
            
            # 模块过滤
            selected_modules = st.multiselect(
                '选择模块',
                df['Module'].unique().tolist()
            )
            
            if selected_modules:
                df = df[df['Module'].isin(selected_modules)]
            
            # 显示数据
            st.subheader('日志数据')
            # 使用 use_container_width=True 让表格占满容器宽度
            # height 参数设置表格高度（像素）
            st.dataframe(
                df,
                use_container_width=True,  # 使用容器宽度
                height=600  # 设置表格高度为600像素
            )
            
            # 显示模块分布
            st.subheader('模块分布')
            st.bar_chart(df['Module'].value_counts())
            
            # 添加每日统计
            add_daily_stats(df)
            
    elif data_type == '按类别细化':
        st.header('按类别细化数据')
        
        # 选择类别
        category = st.selectbox(
            '选择类别',
            ['STORAGE', 'NETWORK', 'SYSTEM', 'VSAN', 'VM', 'UNMATCHED']
        )
        
        df = load_latest_csv(f'vmk-basic-3-refined-{category.lower()}')
        if df is not None:
            st.write(f'{category} 类别总记录数: {len(df)}')
            
            # 时间范围选择
            if 'Time' in df.columns:
                df['Time'] = pd.to_datetime(df['Time'])
                min_time = df['Time'].min()
                max_time = df['Time'].max()
                
                # 转换为日期字符串进行显示和选择
                date_min = min_time.strftime('%Y-%m-%d %H:%M:%S')
                date_max = max_time.strftime('%Y-%m-%d %H:%M:%S')
                
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.text_input('开始时间', date_min)
                with col2:
                    end_date = st.text_input('结束时间', date_max)
                
                try:
                    # 将用户输入转换回datetime
                    start_dt = pd.to_datetime(start_date)
                    end_dt = pd.to_datetime(end_date)
                    
                    # 过滤数据
                    df = df[(df['Time'] >= start_dt) & (df['Time'] <= end_dt)]
                    st.write(f'选定时间范围内的记录数: {len(df)}')
                except:
                    st.error('请输入有效的时间格式：YYYY-MM-DD HH:MM:SS')
            
            # 显示数据
            st.subheader('日志数据')
            # 使用 use_container_width=True 让表格占满容器宽度
            # height 参数设置表格高度（像素）
            st.dataframe(
                df,
                use_container_width=True,  # 使用容器宽度
                height=600  # 设置表格高度为600像素
            )
            
            # 显示模块分布
            if 'Module' in df.columns:
                st.subheader('模块分布')
                st.bar_chart(df['Module'].value_counts())
            
            # 添加每日统计（在模块分布后面）
            add_daily_stats(df)
    
    # 如果没有找到数据，显示警告
    if df is None:
        st.warning('请先运行vmk_main.py生成数据文件')

if __name__ == '__main__':
    main() 