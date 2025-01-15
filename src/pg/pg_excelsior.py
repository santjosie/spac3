import streamlit as st
from utils.excelsior import excelsify, descode
import os

def oapi_to_excel():
    uploaded_file = st.file_uploader(label="Convert OpenAPI documents to MS Excel files",
                                          type=["yaml","yml","json"], accept_multiple_files=False)
    if uploaded_file:
        st.divider()
        excel = excelsify(uploaded_file)
        if excel:
            excel_name, ext = os.path.splitext(uploaded_file.name)
            st.download_button(label='Download',
                               type='primary',
                               data=excel,
                               file_name=excel_name+'.xlsx',
                               mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            st.toast(body="OpenAPI document converted to Excel!", icon=":material/thumb_up:")


oapi_to_excel()
if __name__ == '__main__':
    oapi_to_excel()