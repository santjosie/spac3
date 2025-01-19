import streamlit as st
import yaml
from utils import standardizer, file_handler

def body():
    spec_files = st.file_uploader(label="Add the files to auto-standardize", accept_multiple_files=True, type=["yaml", "yml", "json"])
    if spec_files:
        convert_case = st.toggle(label="Convert case?", value=True)
        error_response = st.toggle(label="Add error response?", value=True)
        pagination = st.toggle(label="Add pagination?", value=True)
        message = st.toggle(label="Add message?", value=True)
        header = st.toggle(label="Add header?", value=True)
        remove_path_server = st.toggle(label="Remove path server?", value=True)
        remove_non_json_content = st.toggle(label="Remove non-json payload content?", value=True)
        if convert_case or error_response or pagination or message or header:
            standardize = st.button(label="Standardize")
            if standardize:
                for spec_file in spec_files:
                    spec_data = file_handler.load_oapi_spec(spec_file)
                    if convert_case:
                        spec_data = standardizer.check_and_convert_casing(spec_data)
                    if error_response:
                        spec_data = standardizer.process_error_response(spec_data)
                    if pagination:
                        spec_data = standardizer.process_pagination(spec_data)
                    if message:
                        spec_data = standardizer.process_message(spec_data)
                    if header:
                        spec_data = standardizer.process_header(spec_data)
                    if remove_path_server:
                        spec_data = standardizer.remove_path_servers(spec_data)
                    if remove_non_json_content:
                        spec_data = standardizer.remove_non_json_content(spec_data)
                    st.download_button(label='Download',
                               type='primary',
                               data=yaml.dump(spec_data),
                               file_name=spec_file.name,
                               mime='application/octet-stream')

body()