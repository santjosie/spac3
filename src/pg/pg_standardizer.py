import streamlit as st
import yaml
import json
from src.utils import standardizer, file_handler, combiner, splitter
import zipfile
from io import BytesIO

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
        convert_case = st.toggle(label="Convert case?", value=False)
        error_response = st.toggle(label="Add error response?", value=False)
        pagination = st.toggle(label="Add pagination?", value=False)
        message = st.toggle(label="Add message?", value=False)
        header = st.toggle(label="Add header?", value=True)
        if header:
            header_content = st.text_area(label="Enter header content in JSON format")
        remove_path_server = st.toggle(label="Remove path server?", value=False)
        remove_non_json_content = st.toggle(label="Remove non-json payload content?", value=False)
        if convert_case or error_response or pagination or message or header or remove_path_server or remove_non_json_content:
            standardize = st.button(label="Standardize")
            if standardize:
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
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
                            if header_content:
                                header_content = json.loads(header_content)
                            spec_data = standardizer.process_header(spec_data, header_content)
                        if remove_path_server:
                            spec_data = standardizer.remove_path_servers(spec_data)
                        if remove_non_json_content:
                            spec_data = standardizer.remove_non_json_content(spec_data)

                        # Save each spec_data to an in-memory file
                        if spec_data:
                            dumped_spec = file_handler.dump_oapi_spec(spec_data)
                            if dumped_spec:  # Ensure the dumped spec is not empty or None
                                zip_file.writestr(spec_file.name, dumped_spec)
                            else:
                                st.warning(f"Failed to process file: {spec_file.name}")

                    zip_file.close()
                    # Prepare the zip file for download
                    zip_buffer.seek(0)
                    if zip_file.namelist():  # Check if the zip file contains any files
                        st.download_button(
                            label="Download",
                            data=zip_buffer.getvalue(),
                            file_name="standardized_openapi_files.zip",
                            mime="application/zip"
                        )
                    else:
                        st.error("No files were added to the zip. Please check the input files or processing steps.")

body()