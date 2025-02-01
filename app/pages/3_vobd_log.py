import streamlit as st
import os
import sys
from pathlib import Path

# Add project root directory to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from app.ui import vobd_view

st.set_page_config(page_title="vobd Log", layout="wide")

def is_valid_vobd_log(filename):
    """Check if it's a valid vobd log file"""
    # Check if filename starts with vobd
    if not filename.lower().startswith('vobd'):
        return False
    
    # Check if file extension is .log or .all
    return filename.lower().endswith(('.log', '.all'))

# File upload
uploaded_file = st.sidebar.file_uploader(
    "Upload Log File",
    type=['log', 'all'],  # Allowed file extensions
    help="Please upload a vobd log file (starting with 'vobd', .log or .all format)"
)

if uploaded_file is not None:
    if is_valid_vobd_log(uploaded_file.name):
        # Save uploaded file
        logs_dir = 'logs'
        os.makedirs(logs_dir, exist_ok=True)
        file_path = os.path.join(logs_dir, uploaded_file.name)
        
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        st.sidebar.success(f'File uploaded: {uploaded_file.name}')
        vobd_view.show(file_path)
    else:
        st.error('Please upload a valid vobd log file (must start with "vobd" and end with .log or .all)')
else:
    st.info('Please upload a vobd log file for analysis') 