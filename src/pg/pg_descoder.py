import streamlit as st
from utils.excelsior import excelsify, descode

def excel_to_oapi():
    excelcol, spec_col = st.columns(2)
    with spec_col:
        uploaded_spec_file = st.file_uploader(label="Upload the open API spec that you want to update the descriptions for ",
                                               type=["yaml", "yml", "json"], accept_multiple_files=False)

    with excelcol:
        uploaded_excel_file = st.file_uploader(label="Upload the open Excel file that you want to merge with your spec ",
                                          type=["xlsx"], accept_multiple_files=False)

    if uploaded_spec_file and uploaded_excel_file:
        st.divider()
        updated_spec_file = descode(uploaded_excel_file, uploaded_spec_file)
        if updated_spec_file:
            st.download_button(label='Download',
                               type = 'primary',
                                data=updated_spec_file,
                                file_name=uploaded_spec_file.name,
                                mime='application/octet-stream')
        st.toast(body="Excel converted to OpenAPI document!", icon=":material/thumb_up:")

excel_to_oapi()
if __name__ == '__main__':
    excel_to_oapi()