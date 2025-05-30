from ruamel.yaml import YAML
import json
import pandas as pd
import io
from io import StringIO
import streamlit as st

def dump_oapi_spec(spec):
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True
    output_stream = StringIO()
    yaml.dump(spec, output_stream)
    return output_stream.getvalue()

def load_oapi_spec(file):
    """
    extracts the content of the OAPI file and stores in memory in a dict format
    :param file:
    :return: the OAPI document contents in dict format
    """
    spec = None
    if file.name.endswith('.yaml') or file.name.endswith('.yml'):
        # Use ruamel.yaml to preserve order
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        spec = yaml.load(file)
    elif file.name.endswith('.json'):
        spec = json.load(file)
    return spec

def write_to_excel(parameters=None, request_body=None, response_body=None, schema_attributes=None):
    """
    writes tables passed as parameters in separate spreadsheets in an Excel file in memory
    :param parameters:
    :param attributes:
    :return:
    """


    df_parameters = pd.DataFrame(parameters) if parameters else None
    df_request_body = pd.DataFrame(request_body) if request_body else None
    df_response_body = pd.DataFrame(response_body) if response_body else None
    df_schemas = pd.DataFrame(schema_attributes) if schema_attributes else None

    output = io.BytesIO()

    # Create a Pandas Excel writer using XlsxWriter as the engin
    with (pd.ExcelWriter(output, engine='openpyxl') as writer):
        if df_parameters is not None and not df_parameters.empty:
            df_parameters.to_excel(writer, sheet_name='parameters', index=False)
        if df_request_body is not None and not df_request_body.empty:
            df_request_body.to_excel(writer, sheet_name='request_body', index=False)
        if df_response_body is not None and not df_response_body.empty:
            df_response_body.to_excel(writer, sheet_name='response_body', index=False)
        if df_schemas is not None and not df_schemas.empty:
            df_schemas.to_excel(writer, sheet_name='schemas', index=False)
        if all(
                df is None or df.empty
                for df in [df_parameters, df_request_body, df_response_body, df_schemas]
        ):
            pd.DataFrame().to_excel(writer, sheet_name='empty_sheet', index=False)

    output.seek(0)

    return output