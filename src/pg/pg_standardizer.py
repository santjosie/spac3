import streamlit as st
import yaml
import json
from utils import standardizer, file_handler, combiner, splitter

def body():
    t_standardizer, t_combiner, t_splitter = st.tabs(["Standardize", "Combine", "Split"])
    with t_standardizer:
        standardize()

    with t_combiner:
        combine()

    with t_splitter:
        split()

def split():
    spec_files = st.file_uploader(label="Upload OpenAPI v3.1.0 File", accept_multiple_files=True, type=["yaml", "yml", "json"])

    if spec_files:
        split = st.button(label="Split")
        if split:
            split_files = []
            for spec_file in spec_files:
                spec_data = file_handler.load_oapi_spec(spec_file)
                split_files.extend(splitter.split_openapi_file(spec_data))

            st.write("Split Complete! Download individual files below:")
            for path, split_spec in split_files:
                st.download_button(
                    label=f"Download {path.replace('/', '_')}.yaml",
                    data=file_handler.dump_oapi_spec(split_spec),
                    file_name=f"{path.replace('/', '_')}.yaml",
                    mime="application/x-yaml"
                )

def combine():
    spec_files = st.file_uploader(label="Add the files to combine", accept_multiple_files=True,
                                  type=["yaml", "yml", "json"])
    if spec_files:
        combine = st.button(label="Combine")
        if combine:
            spec_data = combiner.merge_specs(spec_files)
            st.download_button(label='Download',
                               type='primary',
                               data=yaml.dump(spec_data),
                               file_name=spec_files[0].name,
                               mime='application/octet-stream')

def standardize():
    spec_files = st.file_uploader(label="Add the files to auto-standardize", accept_multiple_files=True, type=["yaml", "yml", "json"])
    if spec_files:
        convert_case = st.toggle(label="Convert case?", value=True)
        error_response = st.toggle(label="Add error response?", value=True)
        pagination = st.toggle(label="Add pagination?", value=True)
        message = st.toggle(label="Add message?", value=True)
        header = st.toggle(label="Add header?", value=True)
        if header:
            header_content = st.text_area(label="Enter header content in JSON format")
        remove_path_server = st.toggle(label="Remove path server?", value=True)
        remove_non_json_content = st.toggle(label="Remove non-json payload content?", value=True)
        combine_into_one = st.toggle(label="Combine into one file?", value=True)
        if combine_into_one:
            combined_name = st.text_input(label="Name of the combined file")
        if convert_case or error_response or pagination or message or header or combined_name or remove_path_server or remove_non_json_content:
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
                        spec_data = standardizer.process_header(spec_data, json.loads(header_content))
                    if remove_path_server:
                        spec_data = standardizer.remove_path_servers(spec_data)
                    if remove_non_json_content:
                        spec_data = standardizer.remove_non_json_content(spec_data)
                    if combine_into_one and combined_name:
                        spec_data = standardizer.combine_paths(spec_data)

                    st.download_button(label='Download',
                               type='primary',
                               data=file_handler.dump_oapi_spec(spec_data), #yaml.dump(spec_data, Dumper=OrderedDumper),
                               file_name=spec_file.name,
                               mime='application/octet-stream')

body()