import yaml
import json
import pandas as pd
import io

def load_oapi_spec(file):
    """
    extracts the content of the OAPI file and stores in memory in a dict format
    :param file:
    :return: the OAPI document contents in dict format
    """
    spec = None
    if file.name.endswith('.yaml') or file.name.endswith('.yml'):
        spec = yaml.safe_load(file)
    elif file.name.endswith('.json'):
        spec = json.load(file)
    return spec

def write_to_excel(parameters, attributes, schema_attributes):
    """
    writes tables passed as parameters in separate spreadsheets in an Excel file in memory
    :param parameters:
    :param attributes:
    :return:
    """
    df_parameters = pd.DataFrame(parameters)
    df_attributes = pd.DataFrame(attributes)
    df_schemas = pd.DataFrame(schema_attributes)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_parameters.to_excel(writer, sheet_name='parameters', index=False)
        df_attributes.to_excel(writer, sheet_name='attributes', index=False)
        df_schemas.to_excel(writer, sheet_name='schemas', index=False)

    output.seek(0)

    return output