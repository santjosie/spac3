import streamlit as st
from utils.excelsior import excelsify, descode
import os

def oapi_to_excel():
    uploaded_files = st.file_uploader(label="Convert OpenAPI documents to MS Excel files",
                                          type=["yaml","yml","json"], accept_multiple_files=True)
    if uploaded_files:
        st.divider()
        for uploaded_file in uploaded_files:
            overall_status_text = "Processing " + uploaded_file.name
            overall_status_bar = st.sidebar.progress(value=0, text=overall_status_text)
            excel = excelsify(uploaded_file)
            if excel:
                excel_name, ext = os.path.splitext(uploaded_file.name)
                st.download_button(label='Download ' + excel_name + '.xlsx',
                                   type='primary',
                                   data=excel,
                                   file_name=excel_name+'.xlsx',
                                   mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                st.toast(body=uploaded_file.name + " converted to " + excel_name + ".xlsx", icon=":material/thumb_up:")
            overall_status_bar.progress(value=1, text=overall_status_text)
            overall_status_bar.empty()

oapi_to_excel()