import yaml
import json
import streamlit as st
from .excel_writer import write_to_excel

VALID_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace', 'connect'}

def load_oapi_spec(file):
    """
    extracts the content of the OAPI file to a dict format
    :param file:
    :return: the OAPI document contents in dict format
    """
    spec = None
    if file.name.endswith('.yaml') or file.name.endswith('.yml'):
        spec = yaml.safe_load(file)
    elif file.name.endswith('.json'):
        spec = json.load(file)
    return spec

#extract the request body schema
def get_parameters(parameters):
    parameters_table = []
    if parameters:
        for parameter in parameters:
            parameters_table.append({"parameter_type": parameter.get('in')
                                        , "name": parameter.get('name')
                                        , "required": parameter.get('required')
                                        , "data_type": parameter.get('schema').get('type')
                                        , "description": parameter.get('schema').get('description')})
        return parameters_table

def get_request_body(request_body, spec):
    if request_body:
        request_body_content = request_body.get('content')
        if 'application/json' in request_body_content:
            schema = request_body_content['application/json'].get('schema', {})
            attributes = extract_attributes(schema, spec)
            return attributes

def resolve_ref(ref, spec):
    """
    Resolve a JSON Reference ($ref) within the OpenAPI specification.
    """
    ref_path = ref.lstrip('#/').split('/')
    result = spec
    for part in ref_path:
        result = result.get(part, {})
    return result, ref_path[-1]

def extract_attributes(schema, spec, parent_path='', visited_refs=None, attributes=None, object_name=None):
    """
    Recursively extract attributes from the schema.
    """
    if visited_refs is None:
        visited_refs = []
    if attributes is None:
        attributes = []

    if '$ref' in schema:
        ref = schema['$ref']
        if ref in visited_refs:
            return attributes  # Avoid infinite recursion
        visited_refs.append(ref)
        resolved_schema, schema_name = resolve_ref(ref, spec)
        return extract_attributes(resolved_schema, spec, parent_path, visited_refs, attributes, schema_name)

    if 'allOf' in schema:
        for subschema in schema['allOf']:
            extract_attributes(subschema, spec, parent_path, visited_refs, attributes)
    elif 'anyOf' in schema:
        for subschema in schema['anyOf']:
            extract_attributes(subschema, spec, parent_path, visited_refs, attributes)
    elif 'oneOf' in schema:
        for subschema in schema['oneOf']:
            extract_attributes(subschema, spec, parent_path, visited_refs, attributes)

    elif schema.get('type') == 'object':
        full_path = f"{parent_path}" if parent_path else object_name
        parent_path = f"{parent_path}" if parent_path else object_name
        attributes.append({
            'full_path': full_path,
            'name': object_name,
            'type': schema.get('type'),
            'description': schema.get('description')
        })
        properties = schema.get('properties', {})
        for prop_name, prop_schema in properties.items():
            full_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
            attr_type = prop_schema.get('type', 'object')
            if attr_type not in ['object', 'array']:
                description = prop_schema.get('description', '')
                # Append attributes
                attributes.append({
                        'full_path': full_path,
                        'name': prop_name,
                        'type': attr_type,
                        'description': description
                    })
            # Recursively process if it's an object or array
            if attr_type in ['object', 'array']:
                extract_attributes(prop_schema, spec, full_path, visited_refs.copy(), attributes, prop_name)
    elif schema.get('type') == 'array':
        full_path = parent_path
        attributes.append({
            'full_path': full_path,
            'name': object_name,
            'type': schema.get('type'),
            'description': schema.get('description')
        })
        items_schema = schema.get('items', {})
        extract_attributes(items_schema, spec, full_path, visited_refs.copy(), attributes, object_name)
    else:
        # Append attributes for native data types
        attributes.append({
            'full_path': parent_path,
            'name': object_name,
            'type': schema.get('type', ''),
            'description': schema.get('description', '')
        })
    return attributes

def get_response(response):
    a=1

def excelsify(file):
    spec = load_oapi_spec(file)
    paths = spec.get('paths', {})
    for path, path_details in paths.items():
        for method, method_details in path_details.items():
            if method in VALID_METHODS:
                # parameters
                parameters = get_parameters(method_details.get('parameters'))
                with st.expander('Parameters'):
                    st.table(parameters)
                request_body = get_request_body(method_details.get('requestBody'), spec)
                with st.expander('Request body'):
                    st.table(request_body)
                # response = get_response()
                excel=write_to_excel(parameters, request_body)

    return excel