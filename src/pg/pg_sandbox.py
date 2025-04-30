import streamlit as st
from src.utils.schema_parser import excelsifyer

def sandbox():
    uploaded_file = st.file_uploader(label="SANDBOX MODE: Convert OpenAPI documents to MS Excel files",
                                          type=["yaml","yml","json"], accept_multiple_files=False)
    if uploaded_file:
        st.divider()
        excel = excelsifyer(uploaded_file)
        if excel:
            st.download_button(label='Download',
                               type='primary',
                               data=excel,
                               file_name='open_api_spec.xlsx',
                               mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

sandbox()
if __name__ == '__main__':
    sandbox()