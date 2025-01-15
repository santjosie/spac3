import streamlit as st
import json
from typing import Dict, List

import yaml
from utils import excelsior as excel

def check_and_convert_casing(openapi_spec: Dict) -> Dict:

    def to_pascal_case(name: str) -> str:
        """Converts a string to PascalCase."""
        return name[0].upper() + name[1:]

    def process_schema(schema: Dict) -> Dict:
        """Processes a single schema to check and convert casing."""
        if 'properties' in schema:
            schema['properties'] = {
                to_pascal_case(key): process_properties(value)
                for key, value in schema['properties'].items()
            }
        return schema

    def process_properties(properties: Dict) -> Dict:
        """Processes properties within a schema."""
        if 'type' in properties and properties['type'] == 'object':
            properties = process_schema(properties)
        return properties

    if 'components' in openapi_spec and 'schemas' in openapi_spec['components']:
        openapi_spec['components']['schemas'] = {
            to_pascal_case(key): process_schema(value)
            for key, value in openapi_spec['components']['schemas'].items()
        }

    return openapi_spec

def body():
    spec = st.file_uploader("Yaml file")
    if spec:
        spec_data = excel.load_oapi_spec(spec)
        openapi_spec_pascal_case = check_and_convert_casing(spec_data)
        st.download_button(label='Download',
                           type='primary',
                           data=yaml.dump(openapi_spec_pascal_case),
                           file_name='open_api_spec.yaml',
                           mime='application/octet-stream')


body()