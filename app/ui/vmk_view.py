import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# 添加项目根目录到Python路径
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from app.processors.vmk.vmk_8_log_1_processor import VMK8LogProcessor
from app.processors.vmk.vmk_8_log_2_filter import VMK8LogFilter
from app.processors.vmk.vmk_8_log_3_refine import VMK8LogRefiner

def add_daily_stats(df):
    """
    添加每日统计图表
    
    功能：
    1. 解析时间戳
    2. 按日期统计日志数量
    3. 生成折线图和数据表格
    
    参数:
        df (pd.DataFrame): 包含Time列的数据框
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
            st.line_chart(daily_counts.set_index('Date'))
            
            # 显示具体数据
            st.subheader('每日统计详情')
            st.dataframe(daily_counts, use_container_width=True, height=200)
        except Exception as e:
            st.error(f'处理时间数据时出错: {str(e)}')

def show(file_path):
    """
    显示VMKernel日志分析界面
    
    处理流程：
    1. 基础处理：解析原始日志
    2. 过滤处理：提取模块信息
    3. 细化处理：按类别分类
    
    参数:
        file_path (str): 日志文件路径
    """
    st.header('VMKernel日志分析')
    
    # === 步骤 1: 基础日志处理 ===
    with st.expander("步骤 1: 基础处理", expanded=True):
        processor = VMK8LogProcessor()
        df_processed = processor.process_log_file(file_path)
        if not df_processed.empty:
            st.success(f"基础处理完成，共 {len(df_processed)} 条记录")
            
            # === 显示数据过滤选项 ===
            st.subheader('过滤选项')
            col1, col2 = st.columns(2)
            # 日志级别过滤（vmkalert/vmkwarning/vmkernel）
            with col1:
                selected_level = st.multiselect(
                    '日志级别',
                    df_processed['LogLevel'].unique().tolist()
                )
            # 日志标签过滤（Al/Wa/In）
            with col2:
                selected_tag = st.multiselect(
                    '日志标签',
                    df_processed['LogTag'].unique().tolist()
                )
            
            # === 应用过滤条件 ===
            filtered_df = df_processed
            if selected_level:
                filtered_df = filtered_df[filtered_df['LogLevel'].isin(selected_level)]
            if selected_tag:
                filtered_df = filtered_df[filtered_df['LogTag'].isin(selected_tag)]
            
            # === 显示数据表格 ===
            st.subheader('日志数据')
            st.dataframe(filtered_df, use_container_width=True, height=600)
            
            # === 显示统计信息 ===
            st.subheader('统计信息')
            col1, col2 = st.columns(2)
            with col1:
                st.write('日志级别分布')
                st.write(filtered_df['LogLevel'].value_counts())
            with col2:
                st.write('日志标签分布')
                st.write(filtered_df['LogTag'].value_counts())
            
            # === 添加每日统计图表 ===
            add_daily_stats(filtered_df)
        else:
            st.error("基础处理失败")
            return
    
    # === 步骤 2: 日志过滤 ===
    with st.expander("步骤 2: 日志过滤", expanded=True):
        filter = VMK8LogFilter()
        # 直接使用DataFrame进行过滤，而不是重新读取文件
        df_filtered = filter.filter_dataframe(df_processed)
        if not df_filtered.empty:
            st.success(f"过滤完成，保留 {len(df_filtered)} 条记录")
            
            # === 模块过滤选项 ===
            selected_modules = st.multiselect(
                '选择模块',
                df_filtered['Module'].unique().tolist()
            )
            
            # 应用模块过滤
            if selected_modules:
                df_filtered = df_filtered[df_filtered['Module'].isin(selected_modules)]
            
            # === 显示过滤后的数据 ===
            st.subheader('日志数据')
            st.dataframe(df_filtered, use_container_width=True, height=600)
            
            # === 显示模块分布 ===
            st.subheader('模块分布')
            st.bar_chart(df_filtered['Module'].value_counts())
            
            # === 添加每日统计 ===
            add_daily_stats(df_filtered)
        else:
            st.error("过滤处理失败")
            return
    
    # === 步骤 3: 按类别细化 ===
    with st.expander("步骤 3: 按类别细化", expanded=True):
        refiner = VMK8LogRefiner()
        # 直接处理DataFrame
        category_dfs = refiner.process_dataframe(df_filtered)
        
        # === 类别选择 ===
        category = st.selectbox(
            '选择类别',
            ['STORAGE', 'NETWORK', 'SYSTEM', 'VSAN', 'VM', 'UNMATCHED']
        )
        
        # === 处理选定类别的数据 ===
        if category in category_dfs and not category_dfs[category].empty:
            df = category_dfs[category]
            st.write(f'{category} 类别总记录数: {len(df)}')
            
            # === 时间范围选择 ===
            if 'Time' in df.columns:
                df['Time'] = pd.to_datetime(df['Time'])
                min_time = df['Time'].min()
                max_time = df['Time'].max()
                
                # 转换为易读的时间格式
                date_min = min_time.strftime('%Y-%m-%d %H:%M:%S')
                date_max = max_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # 时间范围输入
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.text_input('开始时间', date_min)
                with col2:
                    end_date = st.text_input('结束时间', date_max)
                
                try:
                    # 应用时间范围过滤
                    start_dt = pd.to_datetime(start_date)
                    end_dt = pd.to_datetime(end_date)
                    df = df[(df['Time'] >= start_dt) & (df['Time'] <= end_dt)]
                    st.write(f'选定时间范围内的记录数: {len(df)}')
                except:
                    st.error('请输入有效的时间格式：YYYY-MM-DD HH:MM:SS')
            
            # === 显示分类后的数据 ===
            st.subheader('日志数据')
            st.dataframe(df, use_container_width=True, height=600)
            
            # === 显示模块分布 ===
            st.subheader('模块分布')
            st.bar_chart(df['Module'].value_counts())
            
            # === 添加每日统计 ===
            add_daily_stats(df) 