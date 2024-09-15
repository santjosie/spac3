import streamlit as st
# from src.py.utils.oapi3_parser import convert_spec_to_excel
#from ..utils.oapi3_parser import convert_spec_to_excel
from utils.oapi3_parser import convert_spec_to_excel

def header():
    st.header("Welcome to spac3 OpenAPI to Excel converter")
    st.caption("Convert your OpenAPI spec to MS Excel.")

def main():
    st.set_page_config(
        page_title='spac3 | Excel',
        page_icon=':material/home:',
        menu_items={
            'Get help': 'https://www.santhoshjose.dev',
            'About': '# Version: 2.2 #'
        })

    def file_uploader():
        uploaded_file = st.file_uploader(label="Upload the open API spec that you want to convert into Excel",
                                          type=["yaml","yml","json"], accept_multiple_files=False)
        if uploaded_file:
            excel = convert_spec_to_excel(uploaded_file)
            if excel:
                st.download_button(label='Download the spec in Excel format',
                                   data=excel,
                                   file_name='open_api_spec.xlsx',
                                   mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    header()
    file_uploader()

if __name__=="__main__":
    main()