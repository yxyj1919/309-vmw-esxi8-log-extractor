import streamlit as st

st.set_page_config(
    page_title="VMware ESXi Log Analyzer",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("VMware ESXi Log Analyzer")
    st.write("Welcome to VMware ESXi Log Analyzer. Please select a log type from the sidebar to begin analysis.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader('vmkernel log analyzer')
        st.info('Analyze system core logs, including storage, network, system, etc.')
        
    with col2:
        st.subheader('vmkwarning log analyzer')
        st.info('Focus on the analysis of system warning information, helping you to find potential problems in time.')
        
    with col3:
        st.subheader('vobd log analyzer')
        st.info('Analyze system logs related to system boot and diagnosis.')

if __name__ == '__main__':
    main() 