import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import os
from datetime import datetime

# 添加项目根目录到Python路径
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from app.processors.vmk.vmk_8_log_1_processor import VMK8LogProcessor
from app.processors.vmk.vmk_8_log_2_filter import VMK8LogFilter
from app.processors.vmk.vmk_8_log_3_refiner import VMK8LogRefiner
from app.processors.vmk.vmk_8_modules_manager import VMKModulesManager

def add_daily_stats(df):
    """
    Add daily statistics chart
    
    Features:
    1. Parse timestamps
    2. Count logs by date
    3. Generate line chart and data table
    
    Args:
        df (pd.DataFrame): DataFrame containing Time column
    """
    if 'Time' in df.columns:
        try:
            # 创建一个明确的副本
            df_stats = df.copy()
            # 在副本上进行操作
            df_stats['Time'] = pd.to_datetime(df_stats['Time'], format='ISO8601')
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

def cleanup_output_files():
    """清理输出文件夹中的临时文件"""
    output_dir = 'output'
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith('.csv'):
                file_path = os.path.join(output_dir, file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"清理文件失败: {file_path}, 错误: {str(e)}")

def show(file_path):
    """
    Display VMKernel log analysis interface
    
    Process flow:
    1. Basic processing: Parse raw logs
    2. Filter processing: Extract module information
    3. Refinement: Categorize by type
    
    Args:
        file_path (str): Log file path
    """
    # 在函数开始就初始化 session state
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
        st.session_state.debug_clicks = 0

    try:
        # 在处理开始前清理旧文件
        if not st.session_state.get('debug_mode', False):  # 使用 get 方法更安全
            cleanup_output_files()
        
        # Create a title with hidden debug trigger
        col1, col2 = st.columns([0.97, 0.03])
        with col1:
            st.header('vmkernel Log Analysis')
        with col2:
            if st.button("⚙️", key="debug_trigger", help="System Settings"):
                st.session_state.debug_clicks += 1
                if st.session_state.debug_clicks >= 3:
                    st.session_state.debug_mode = True
                    st.session_state.debug_clicks = 0
                    st.rerun()
        
        # Display exit debug mode button
        if st.session_state.debug_mode:
            if st.sidebar.button("Exit Debug Mode"):
                st.session_state.debug_mode = False
                st.rerun()

        # === Step 1: Basic Log Processing ===
        with st.expander("Step 1: Basic Processing", expanded=True):
            processor = VMK8LogProcessor()
            df_processed = processor.process_log_file(file_path)
            if not df_processed.empty:
                st.success(f"Basic processing completed, {len(df_processed)} records in total")
                
                # === Display Filter Options ===
                st.subheader('Filter Options')
                col1, col2 = st.columns(2)
                # Log level filter
                with col1:
                    selected_level = st.multiselect(
                        'Log Level',
                        df_processed['LogLevel'].unique().tolist()
                    )
                # Log tag filter
                with col2:
                    selected_tag = st.multiselect(
                        'Log Tag',
                        df_processed['LogTag'].unique().tolist()
                    )
                
                # === Apply Filters ===
                filtered_df = df_processed
                if selected_level:
                    filtered_df = filtered_df[filtered_df['LogLevel'].isin(selected_level)]
                if selected_tag:
                    filtered_df = filtered_df[filtered_df['LogTag'].isin(selected_tag)]
                
                # === Display Data Table ===
                st.subheader('Log Data')
                st.dataframe(filtered_df, use_container_width=True, height=600)
                
                # === Display Statistics ===
                st.subheader('Statistics')
                col1, col2 = st.columns(2)
                with col1:
                    st.write('Log Level Distribution')
                    st.write(filtered_df['LogLevel'].value_counts())
                with col2:
                    st.write('Log Tag Distribution')
                    st.write(filtered_df['LogTag'].value_counts())
                
                # === Add Daily Statistics Chart ===
                add_daily_stats(filtered_df)
            else:
                st.error("Basic processing failed")
                return
        
        # === Add Step 2 Toggle ===
        enable_step2 = st.checkbox('Enable Step 2: Log Filtering', value=False)
        
        # === Step 2: Log Filtering ===
        if enable_step2:
            with st.expander("Step 2: Log Filtering", expanded=True):
                filter = VMK8LogFilter()
                df_filtered = filter.filter_dataframe(df_processed)
                if not df_filtered.empty:
                    st.success(f"Filtering completed, {len(df_filtered)} records retained")
                    
                    # === Module Filter Options ===
                    selected_modules = st.multiselect(
                        'Select Modules',
                        df_filtered['Module'].unique().tolist()
                    )
                    
                    # Apply module filter
                    if selected_modules:
                        df_filtered = df_filtered[df_filtered['Module'].isin(selected_modules)]
                    
                    # === Display Filtered Data ===
                    st.subheader('Log Data')
                    st.dataframe(df_filtered, use_container_width=True, height=600)
                    
                    # === Display Module Distribution ===
                    st.subheader('Module Distribution')
                    st.bar_chart(df_filtered['Module'].value_counts())
                    
                    # === Add Daily Statistics ===
                    add_daily_stats(df_filtered)
                else:
                    st.error("Filter processing failed")
                    return
        else:
            df_filtered = df_processed
        
        # === Add Step 3 Toggle ===
        enable_step3 = st.checkbox('Enable Step 3: Category Refinement', value=False)
        
        # === Step 3: Category Refinement ===
        if enable_step3:
            with st.expander("Step 3: Category Refinement", expanded=True):
                refiner = VMK8LogRefiner()
                category_dfs = refiner.process_dataframe(df_filtered)
                
                # === Category Selection ===
                categories = ['STORAGE', 'NETWORK', 'SYSTEM', 'VSAN', 'VM', 'UNMATCHED']
                category = st.selectbox(
                    'Select Category',
                    categories,
                    key='category_selector'
                )
                
                # === Process Selected Category Data ===
                if category_dfs:
                    if category in category_dfs:
                        df = category_dfs[category]
                        if not df.empty:
                            st.success(f'{category} category total records: {len(df)}')
                            
                            # === Time Range Selection ===
                            if 'Time' in df.columns:
                                # 确保时间列是 datetime 类型
                                if not pd.api.types.is_datetime64_any_dtype(df['Time']):
                                    df['Time'] = pd.to_datetime(df['Time'], utc=True)
                                
                                min_time = df['Time'].min()
                                max_time = df['Time'].max()
                                
                                # 转换为本地时间显示
                                date_min = min_time.tz_localize(None).strftime('%Y-%m-%d %H:%M:%S')
                                date_max = max_time.tz_localize(None).strftime('%Y-%m-%d %H:%M:%S')
                                
                                # 使用日期时间选择器而不是文本输入
                                col1, col2 = st.columns(2)
                                with col1:
                                    start_date = st.text_input('Start Time (UTC)', date_min)
                                with col2:
                                    end_date = st.text_input('End Time (UTC)', date_max)
                                
                                try:
                                    # 转换输入的时间为 UTC
                                    start_dt = pd.to_datetime(start_date).tz_localize('UTC')
                                    end_dt = pd.to_datetime(end_date).tz_localize('UTC')
                                    
                                    # 应用时间范围过滤
                                    mask = (df['Time'] >= start_dt) & (df['Time'] <= end_dt)
                                    df = df[mask]
                                    
                                    if len(df) > 0:
                                        st.write(f'Records in selected time range: {len(df)}')
                                    else:
                                        st.warning('No records found in the selected time range')
                                    
                                except Exception as e:
                                    st.error(f'Please enter valid time format: YYYY-MM-DD HH:MM:SS ({str(e)})')
                            
                            # === Display Categorized Data ===
                            st.subheader('Log Data')
                            st.dataframe(df, use_container_width=True, height=600)
                            
                            # === Add Download Button for Complete Logs ===
                            if 'CompleteLog' in df.columns:
                                st.subheader('Download Filtered Logs')
                                # Prepare logs for download
                                logs_text = '\n'.join(df['CompleteLog'].tolist())
                                st.download_button(
                                    label="Download Raw Logs",
                                    data=logs_text,
                                    file_name=f"vmkernel_{category.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                                    mime="text/plain"
                                )
                            
                            # === Display Module Distribution ===
                            if len(df) > 0:
                                st.subheader('Module Distribution')
                                st.bar_chart(df['Module'].value_counts())
                                
                                # === Add Daily Statistics ===
                                add_daily_stats(df)
                        else:
                            st.warning(f'No data in {category} category')
                    else:
                        st.warning(f'No data found for {category} category')
                else:
                    st.error("Category processing failed")

        # Add module management functionality
        if st.session_state.debug_mode:
            with st.expander("Module Management", expanded=False):
                st.info("🛠️ Debug Mode Activated")
                manager = VMKModulesManager()
                
                # Display current modules
                modules = manager.get_all_modules()
                st.write("Currently Defined Modules:")
                for category, module_list in modules.items():
                    st.subheader(category)
                    for module in module_list:
                        st.text(f"- {module}")
                
                # Add new module
                st.subheader("Add New Module")
                category = st.selectbox("Select Category", list(modules.keys()))
                new_module = st.text_input("Module Name")
                if st.button("Add"):
                    if manager.add_module(category, new_module):
                        st.success("Added Successfully")
                    else:
                        st.error("Add Failed")
                
                # Export functionality
                st.subheader("Export Modules")
                if st.button("Export to CSV"):
                    csv_path = os.path.join(manager.root_dir, 'data', 'dicts', 'exports', 
                                          f'vmk_modules_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
                    if manager.export_to_csv(csv_path):
                        st.success(f"Exported to: {csv_path}")
                    else:
                        st.error("Export Failed")

    finally:
        # 在处理结束后清理临时文件（非调试模式）
        if not st.session_state.get('debug_mode', False):  # 使用 get 方法更安全
            cleanup_output_files() 