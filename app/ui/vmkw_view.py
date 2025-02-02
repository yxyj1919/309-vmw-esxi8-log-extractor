import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import os
from datetime import datetime

# Add project root directory to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from app.processors.vmkw.vmkw_8_log_1_processor import VMKW8LogProcessor
from app.processors.vmkw.vmkw_8_log_2_refiner import VMKW8LogRefiner
from app.processors.vmk.vmk_8_modules_manager import VMKModulesManager
from app.utils.report_generator import ReportGenerator

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
            
            # 确保时间列是 datetime 类型
            if not pd.api.types.is_datetime64_any_dtype(df_stats['Time']):
                df_stats['Time'] = pd.to_datetime(df_stats['Time'], utc=True)
            
            # 使用 UTC 时间的日期部分进行分组
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
            if file.startswith('vmkw-') and file.endswith('.csv'):
                file_path = os.path.join(output_dir, file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"清理文件失败: {file_path}, 错误: {str(e)}")

def show(file_path):
    """
    Display vmkwarning log analysis interface
    
    Process flow:
    1. Basic processing: Parse raw logs
    2. Filter processing: Extract module information
    3. Refinement: Categorize by type
    
    Args:
        file_path (str): Log file path
    """
    # Store debug mode state in Session State
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
        st.session_state.debug_clicks = 0
    
    # Create a title with hidden debug trigger
    col1, col2 = st.columns([0.97, 0.03])
    with col1:
        st.header('vmkwarning Log Analysis')
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

    try:
        # 在处理开始前清理旧文件
        if not st.session_state.get('debug_mode', False):
            cleanup_output_files()

        # === Step 1: Basic Log Processing ===
        with st.expander("Step 1: Basic Processing", expanded=True):
            processor = VMKW8LogProcessor()
            df_processed = processor.process_log_file(file_path)
            
            if df_processed is not None and not df_processed.empty:
                st.success(f"Basic processing completed, {len(df_processed)} records in total")
                
                # === Display Filter Options ===
                st.subheader('Filter Options')
                col1, col2, col3 = st.columns(3)
                
                # Log level filter
                with col1:
                    if 'AlarmLevel' in df_processed.columns:
                        selected_alarm_level = st.multiselect(
                            'Alarm Level',
                            df_processed['AlarmLevel'].unique().tolist()
                        )
                
                # Log tag filter
                with col2:
                    if 'LogTag' in df_processed.columns:
                        selected_tag = st.multiselect(
                            'Log Tag',
                            df_processed['LogTag'].unique().tolist()
                        )
                
                # Module filter
                with col3:
                    if 'Module' in df_processed.columns:
                        selected_module = st.multiselect(
                            'Module',
                            df_processed['Module'].unique().tolist()
                        )
                
                # === Apply Filters ===
                filtered_df = df_processed
                if selected_alarm_level:
                    filtered_df = filtered_df[filtered_df['AlarmLevel'].isin(selected_alarm_level)]
                if selected_tag:
                    filtered_df = filtered_df[filtered_df['LogTag'].isin(selected_tag)]
                if selected_module:
                    filtered_df = filtered_df[filtered_df['Module'].isin(selected_module)]
                
                # === Display Data Table ===
                st.subheader('Log Data')
                st.dataframe(filtered_df, use_container_width=True, height=600)
                
                # === Display Statistics ===
                st.subheader('Statistics')
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if 'AlarmLevel' in filtered_df.columns:
                        st.write('Alarm Level Distribution')
                        st.write(filtered_df['AlarmLevel'].value_counts())
                
                with col2:
                    if 'LogTag' in filtered_df.columns:
                        st.write('Log Tag Distribution')
                        st.write(filtered_df['LogTag'].value_counts())
                
                with col3:
                    if 'Module' in filtered_df.columns:
                        st.write('Module Distribution')
                        st.write(filtered_df['Module'].value_counts())
                
                # === Add Daily Statistics Chart ===
                add_daily_stats(filtered_df)
                
                # === Download Processed Data ===
                st.subheader('Download Processed Data')
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"vmkwarning_processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.error("Basic processing failed")
                return 

        # === Add Step 2 Toggle ===
        enable_step2 = st.checkbox('Enable Step 2: Category Refinement', value=False)

        # === Step 2: Category Refinement ===
        if enable_step2:
            with st.expander("Step 2: Category Refinement", expanded=True):
                refiner = VMKW8LogRefiner()
                
                # 添加调试信息显示区域
                if st.session_state.debug_mode:
                    debug_container = st.empty()
                
                category_dfs = refiner.process_dataframe(filtered_df)
                
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
                                    file_name=f"vmkwarning_{category.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
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
                manager = VMKModulesManager()  # 使用相同的模块管理器
                
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

        # Add report export functionality
        st.sidebar.markdown("---")
        st.sidebar.subheader("Export Report")
        report_format = st.sidebar.selectbox(
            "Report Format",
            ["HTML", "PDF"],
            key="report_format"
        )
        
        if st.sidebar.button("Generate Report"):
            with st.spinner("Generating report..."):
                try:
                    # Initialize report generator
                    generator = ReportGenerator("vmkwarning")
                    
                    # Generate HTML report
                    html_content = generator.generate_html(
                        df_processed,
                        filtered_df=filtered_df,
                        category_dfs=category_dfs if 'category_dfs' in locals() else None
                    )
                    
                    # Generate output filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"vmkwarning_report_{timestamp}"
                    
                    if report_format == "HTML":
                        # Provide HTML download
                        st.sidebar.download_button(
                            "Download HTML Report",
                            html_content,
                            file_name=f"{filename}.html",
                            mime="text/html"
                        )
                    else:
                        # Generate PDF
                        pdf_path = os.path.join('reports', f"{filename}.pdf")
                        os.makedirs('reports', exist_ok=True)
                        if generator.generate_pdf(html_content, pdf_path):
                            with open(pdf_path, 'rb') as f:
                                st.sidebar.download_button(
                                    "Download PDF Report",
                                    f.read(),
                                    file_name=f"{filename}.pdf",
                                    mime="application/pdf"
                                )
                        else:
                            st.sidebar.error("PDF generation failed")
                    
                    st.sidebar.success("Report generated successfully!")
                except Exception as e:
                    st.sidebar.error(f"Error generating report: {str(e)}") 

    finally:
        # 在处理结束后清理临时文件（非调试模式）
        if not st.session_state.get('debug_mode', False):
            cleanup_output_files() 