import streamlit as st
from src.utils.excelsior import excelsify, descode

def main():
    st.set_page_config(
        page_title='spac3 | Home',
        page_icon=':twisted_rightwards_arrows:',
        layout='wide',
        menu_items={
            'Get help': 'https://www.santhoshjose.dev',
            'Report a bug': 'https://www.santhoshjose.dev',
            'About': '# Version: 2.2 #'
        })
    st.header("Spac3!")
    st.caption("OpenAPI spec management platform")

def converter_tabs():
    toexceltab, tospectab = st.tabs(["OAPI 2 Excel", "Excel 2 OAPI"])

    with toexceltab:
        oapi_to_excel()

    with tospectab:
        excel_to_oapi()

def oapi_to_excel():
    uploaded_file = st.file_uploader(label="Convert OpenAPI documents to MS Excel files",
                                          type=["yaml","yml","json"], accept_multiple_files=False)
    if uploaded_file:
        st.divider()
        excel = excelsify(uploaded_file)
        if excel:
            st.download_button(label='Download',
                               type='primary',
                               data=excel,
                               file_name='open_api_spec.xlsx',
                               mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def excel_to_oapi():
    st.subheader("Excel 2 OpenAPI")
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
                                file_name='open_api_spec.yaml',
                                mime='application/octet-stream')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
    converter_tabs()