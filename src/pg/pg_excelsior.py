import streamlit as st
from src.utils.excelsior import excelsify
import os
import zipfile
from io import BytesIO

def oapi_to_excel():
    uploaded_files = st.file_uploader(label="Convert OpenAPI documents to MS Excel files",
                                          type=["yaml","yml","json"], accept_multiple_files=True)
    if uploaded_files:
        st.divider()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for uploaded_file in uploaded_files:
                overall_status_text = "Processing " + uploaded_file.name
                overall_status_bar = st.sidebar.progress(value=0, text=overall_status_text)
                excel = excelsify(uploaded_file)
                if excel:
                    excel_name, ext = os.path.splitext(uploaded_file.name)
                    zip_file.writestr(excel_name + ".xlsx", excel.getvalue())
                    st.toast(body=uploaded_file.name + " converted to " + excel_name + ".xlsx",
                             icon=":material/thumb_up:")

                overall_status_bar.progress(value=1, text=overall_status_text)
                overall_status_bar.empty()
        zip_buffer.seek(0)

        if len(uploaded_files) == 1 and excel:
            st.download_button(
                label="Download as Excel",
                data=excel,
                file_name=excel_name + '.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        elif len(uploaded_files) > 1 and zip_buffer:
            st.download_button(
                label="Download All as ZIP",
                data=zip_buffer.getvalue(),
                file_name="converted_excel_files.zip",
                mime="application/zip"
            )

oapi_to_excel()