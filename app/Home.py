import streamlit as st

st.set_page_config(
    page_title="VMware ESXi Log Analyzer",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("ESXi Log Analyzer (v0.1.0)")
    st.write("Welcome to ESXi Log Analyzer. Please select a log type from the sidebar to begin analysis.")
    
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
    
    # 添加页脚信息
    st.markdown("---")
    st.markdown(
        """
        <div style="position: fixed; bottom: 0; right: 0; padding: 10px;">
            <p style="color: gray; font-size: 0.8em;">
                Bug Report: <a href="mailto:chang.wang@broadcom.com">chang.wang@broadcom.com</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == '__main__':
    main() 