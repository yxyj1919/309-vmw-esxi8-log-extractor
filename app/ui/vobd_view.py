import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add project root directory to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from app.processors.vobd.vobd_8_log_1_processor import VOBD8LogProcessor
from app.processors.vobd.vobd_8_log_2_filter import VOBD8LogFilter
from app.processors.vobd.vobd_8_problem_modules_manager import VOBDProblemModulesManager

def is_debug_mode():
    """检查是否处于调试模式"""
    return os.getenv('VOBD_DEBUG') == 'true' or \
           os.path.exists(os.path.join(root_dir, '.debug'))

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
    if 'Time' in df.columns and not df.empty:
        try:
            # Parse time in ISO format
            df['Time'] = pd.to_datetime(df['Time'])
            # Extract date part
            df['Date'] = df['Time'].dt.date
            # Group by date
            daily_counts = df.groupby('Date').size().reset_index()
            daily_counts.columns = ['Date', 'Count']
            
            # Display daily statistics chart
            st.subheader('Daily Log Count Statistics')
            st.line_chart(daily_counts.set_index('Date'))
            
            # Display detailed data
            st.subheader('Daily Statistics Details')
            st.dataframe(daily_counts, use_container_width=True, height=200)
        except Exception as e:
            st.error(f'Error processing time data: {str(e)}')

def show(file_path):
    """
    Display VOBD log analysis interface
    
    Process flow:
    1. Basic processing: Parse raw logs
    2. Problem log filtering: Extract and analyze problem logs
    
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
        st.header('vobd Log Analysis')
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
        processor = VOBD8LogProcessor(upload_folder='logs')
        df_processed = processor.process_log_file(file_path)
        
        if df_processed is not None and not df_processed.empty:
            st.success(f"Basic processing completed, {len(df_processed)} records in total")
            
            # === Display Filter Options ===
            st.subheader('Filter Options')
            col1, col2 = st.columns(2)
            
            # Level filter
            with col1:
                if 'Level' in df_processed.columns:
                    selected_level = st.multiselect(
                        'Log Level',
                        df_processed['Level'].unique().tolist()
                    )
            
            # Module filter
            with col2:
                if 'Module' in df_processed.columns:
                    selected_module = st.multiselect(
                        'Module',
                        df_processed['Module'].unique().tolist()
                    )
            
            # === Apply Filters ===
            filtered_df = df_processed
            if selected_level:
                filtered_df = filtered_df[filtered_df['Level'].isin(selected_level)]
            if selected_module:
                filtered_df = filtered_df[filtered_df['Module'].isin(selected_module)]
            
            # === Display Data Table ===
            st.subheader('Log Data')
            st.dataframe(filtered_df, use_container_width=True, height=600)
            
            # === Display Statistics ===
            st.subheader('Statistics')
            col1, col2 = st.columns(2)
            with col1:
                if 'Level' in filtered_df.columns:
                    st.write('Log Level Distribution')
                    st.write(filtered_df['Level'].value_counts())
            with col2:
                if 'Module' in filtered_df.columns:
                    st.write('Module Distribution')
                    st.write(filtered_df['Module'].value_counts())
            
            # === Add Daily Statistics Chart ===
            add_daily_stats(filtered_df)
        else:
            st.error("Basic processing failed")
            return
    
    # === Add Step 2 Toggle ===
    enable_step2 = st.checkbox('Enable Step 2: Problem Log Filtering', value=False)

    # === Step 2: Problem Log Filtering ===
    if enable_step2:
        # Debug Mode Module Management
        if st.session_state.debug_mode:
            st.subheader("Module Management")
            st.info("🛠️ Debug Mode Activated")
            manager = VOBDProblemModulesManager()
            
            # Display current modules
            modules = manager.get_all_modules()
            st.write("Currently Defined Modules:")
            for module_id, desc in modules.items():
                st.text(f"{module_id}: {desc}")
            
            # Add new module
            st.subheader("Add New Module")
            new_module_id = st.text_input("Module ID")
            new_module_desc = st.text_input("Description")
            if st.button("Add"):
                if manager.add_module(new_module_id, new_module_desc):
                    st.success("Added Successfully")
                else:
                    st.error("Add Failed")
            
            # Export functionality
            st.subheader("Export Modules")
            if st.button("Export to CSV"):
                csv_path = os.path.join(manager.root_dir, 'data', 'dicts', 'exports', 
                                      f'problem_modules_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
                if manager.export_to_csv(csv_path):
                    st.success(f"Exported to: {csv_path}")
                else:
                    st.error("Export Failed")
            
            st.markdown("---")  # Add separator

        # Problem Log Analysis
        with st.expander("Step 2: Problem Log Filtering", expanded=True):
            filter = VOBD8LogFilter()
            
            # === Process Unknown Problem Logs ===
            unknown_problems = filter.get_unknown_problems(df_processed)
            if not unknown_problems.empty:
                st.warning(f"Found {len(unknown_problems)} unknown problem logs")
                
                # Use checkbox to control unknown problem display
                if st.checkbox("Show Unknown Problem Logs", False, key="show_unknown_problems_1"):
                    st.dataframe(unknown_problems, use_container_width=True, height=400)
                    
                    # Provide download functionality
                    csv = unknown_problems.to_csv(index=False)
                    st.download_button(
                        label="Download Unknown Problem Logs",
                        data=csv,
                        file_name="unknown_problems.csv",
                        mime="text/csv"
                    )
            
            st.markdown("---")  # Add separator
            
            # === Process Known Problem Logs ===
            df_filtered = filter.filter_problems(df_processed)
            
            if not df_filtered.empty:
                st.success(f"Filtering completed, found {len(df_filtered)} known problem logs")
                
                # === Add Module Filter Options ===
                if 'Module' in df_filtered.columns:
                    selected_problem_modules = st.multiselect(
                        'Select Problem Modules to View',
                        df_filtered['Module'].unique().tolist(),
                        key='problem_modules_filter'
                    )
                    
                    # Apply module filter
                    if selected_problem_modules:
                        df_filtered = df_filtered[df_filtered['Module'].isin(selected_problem_modules)]
                        st.write(f"Selected {len(df_filtered)} related logs")
                
                # === Display Filtered Data ===
                st.subheader('Problem Log Data')
                st.dataframe(df_filtered, use_container_width=True, height=600)
                
                # === Add Download Button for Complete Logs ===
                if 'CompleteLog' in df_filtered.columns:
                    st.subheader('Download Filtered Logs')
                    # Prepare logs for download
                    logs_text = '\n'.join(df_filtered['CompleteLog'].tolist())
                    st.download_button(
                        label="Download Raw Logs",
                        data=logs_text,
                        file_name=f"vobd_problems_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                        mime="text/plain"
                    )
                
                # === Display Module Distribution ===
                if 'Module' in df_filtered.columns:
                    st.subheader('Problem Module Distribution')
                    st.bar_chart(df_filtered['Module'].value_counts())
                
                # === Add Daily Statistics ===
                add_daily_stats(df_filtered)
                
                # Also add download button for unknown problems
                if not unknown_problems.empty and 'CompleteLog' in unknown_problems.columns:
                    # Use checkbox to control unknown problem display with a different key
                    if st.checkbox("Show Unknown Problem Logs", False, key="show_unknown_problems_2"):
                        st.dataframe(unknown_problems, use_container_width=True, height=400)
                        
                        st.subheader('Download Unknown Problem Logs')
                        # Prepare logs for download
                        unknown_logs_text = '\n'.join(unknown_problems['CompleteLog'].tolist())
                        st.download_button(
                            label="Download Unknown Problem Logs",
                            data=unknown_logs_text,
                            file_name=f"vobd_unknown_problems_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                            mime="text/plain",
                            key="unknown_problems_download"
                        )
            else:
                st.info("No problem logs found") 