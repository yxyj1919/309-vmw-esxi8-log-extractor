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
        # 在调试模式下设置环境变量
        if st.session_state.debug_mode:
            os.environ['VMK_DEBUG'] = 'true'
        else:
            os.environ['VMK_DEBUG'] = 'false'

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

                # Log tag filter (移到左侧)
                with col1:
                    # 获取所有唯一的日志标签
                    log_tags = sorted(df_processed['LogTag'].unique().tolist())
                    selected_tag = st.multiselect(
                        'Log Tag',
                        options=log_tags,
                        default=log_tags,  # 默认选中所有标签
                        help="Select one or more log tags"
                    )

                # Log level filter (移到右侧)
                with col2:
                    # 获取所有唯一的日志级别
                    log_levels = sorted(df_processed['LogLevel'].unique().tolist())
                    selected_level = st.multiselect(
                        'Log Level',
                        options=log_levels,
                        default=log_levels,  # 默认选中所有级别
                        help="Select one or more log levels"
                    )
                
                # === Apply Filters ===
                filtered_df = df_processed
                if selected_tag:  # 先应用标签过滤
                    filtered_df = filtered_df[filtered_df['LogTag'].isin(selected_tag)]
                if selected_level:  # 再应用级别过滤
                    filtered_df = filtered_df[filtered_df['LogLevel'].isin(selected_level)]
                
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
                
                # 添加调试信息显示区域
                if st.session_state.debug_mode:
                    debug_container = st.empty()
                    
                category_dfs = refiner.process_dataframe(df_filtered)
                
                # 在调试模式下显示分类信息
                if st.session_state.debug_mode and category_dfs:
                    with debug_container:
                        st.subheader("Debug Information")
                        st.text("分类结果统计：")
                        for category, df in category_dfs.items():
                            st.text(f"{category}: {len(df)} records")
                            if not df.empty:
                                st.text("Modules:")
                                st.text(df['Module'].unique())
                        st.markdown("---")
                
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
                            
                            # === Display Categorized Data ===
                            st.subheader('Log Data')
                            try:
                                # 确保所有列都能正确显示
                                st.dataframe(
                                    data=df.copy(),  # 使用数据的副本
                                    use_container_width=True,
                                    height=600,
                                    column_config={
                                        'Time': st.column_config.DatetimeColumn(
                                            'Time',
                                            format='YYYY-MM-DD HH:mm:ss.SSS',
                                            help='Log timestamp'
                                        ),
                                        'LogTag': st.column_config.TextColumn(
                                            'Log Tag',
                                            width='medium',
                                            help='Log tag information'
                                        ),
                                        'LogLevel': st.column_config.TextColumn(
                                            'Log Level',
                                            width='small',
                                            help='Log level'
                                        ),
                                        'CPU': st.column_config.TextColumn(
                                            'CPU',
                                            width='medium',
                                            help='CPU information'
                                        ),
                                        'Module': st.column_config.TextColumn(
                                            'Module',
                                            width='medium',
                                            help='Module name'
                                        ),
                                        'Log': st.column_config.TextColumn(
                                            'Log Message',
                                            width='large',
                                            help='Log message content'
                                        ),
                                        'CompleteLog': st.column_config.TextColumn(
                                            'Complete Log',
                                            width='large',
                                            help='Complete log entry'
                                        )
                                    }
                                )
                            except Exception as e:
                                st.error(f"Error displaying data: {str(e)}")
                            
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
            st.markdown("---")
            st.subheader("🛠️ Module Management")
            manager = VMKModulesManager()
            
            # 显示当前模块
            modules = manager.get_all_modules()
            st.write("Currently Defined Modules:")
            
            # 使用选项卡而不是嵌套的expander
            module_tabs = st.tabs(list(modules.keys()))
            for tab, category in zip(module_tabs, modules.keys()):
                with tab:
                    module_list = modules[category]
                    st.text(f"Total: {len(module_list)} modules")
                    if module_list:
                        st.code('\n'.join(f"- {module}" for module in sorted(module_list)))
            
            # 添加新模块（支持批量）
            st.markdown("---")
            st.subheader("Add New Modules")
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox("Select Category", list(modules.keys()))
            with col2:
                input_type = st.radio("Input Type", ["Single", "Batch"], horizontal=True)
            
            if input_type == "Single":
                new_module = st.text_input("Module Name")
                if st.button("Add Single Module"):
                    if manager.add_module(category, new_module):
                        st.success("Added Successfully")
                    else:
                        st.error("Add Failed")
            else:
                new_modules = st.text_area(
                    "Module Names (one per line)",
                    height=150,
                    help="Enter module names, one per line"
                )
                if st.button("Add Multiple Modules"):
                    module_list = [m.strip() for m in new_modules.split('\n') if m.strip()]
                    success_count, total = manager.add_modules_batch(category, module_list)
                    if success_count > 0:
                        st.success(f"Successfully added {success_count} out of {total} modules")
                    else:
                        st.error(f"Failed to add any modules out of {total}")

    finally:
        # 在处理结束后清理临时文件（非调试模式）
        if not st.session_state.get('debug_mode', False):  # 使用 get 方法更安全
            cleanup_output_files() 