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
            parameters_table.append({"Parameter type": parameter.get('in')
                                        , "Name": parameter.get('name')
                                        , "Required": parameter.get('required')
                                        , "Data-type": parameter.get('schema').get('type')
                                        , "Description": parameter.get('schema').get('description')})
        return parameters_table

def get_request_body(request_body, spec):
    if request_body:
        request_body_content = request_body.get('content')
        if 'application/json' in request_body_content:
            schema = request_body_content['application/json'].get('schema', {})
            if '$ref' in schema:
                ref = schema['$ref']
                attributes = schema_traversal(ref, spec)
                return attributes

def schema_traversal(schema_ref, spec):
    response_schema = resolve_ref(schema_ref, spec)
    attributes = extract_attributes(response_schema, spec)
    return attributes

def resolve_ref(ref, spec):
    """
    Resolve a JSON Reference ($ref) within the OpenAPI specification.
    """
    ref_path = ref.lstrip('#/').split('/')
    result = spec
    for part in ref_path:
        result = result.get(part, {})
    return result

def extract_attributes(schema, spec, parent_path='', visited_refs=None, attributes=None):
    """
    Recursively extract attributes from the schema.
    """
    if visited_refs is None:
        visited_refs = set()
    if attributes is None:
        attributes = []

    if '$ref' in schema:
        ref = schema['$ref']
        if ref in visited_refs:
            return attributes  # Avoid infinite recursion
        visited_refs.add(ref)
        resolved_schema = resolve_ref(ref, spec)
        return extract_attributes(resolved_schema, spec, parent_path, visited_refs, attributes)

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
        properties = schema.get('properties', {})
        for prop_name, prop_schema in properties.items():
            full_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
            attr_type = prop_schema.get('type', 'object')
            description = prop_schema.get('description', '')
            attributes.append({
                'parent': parent_path,
                'name': prop_name,
                'type': attr_type,
                'description': description
            })
            extract_attributes(prop_schema, spec, full_path, visited_refs.copy(), attributes)
    elif schema.get('type') == 'array':
        items_schema = schema.get('items', {})
        extract_attributes(items_schema, spec, parent_path, visited_refs.copy(), attributes)
    else:
        # For primitive types
        attr_type = schema.get('type', 'object')
        description = schema.get('description', '')
        attributes.append({
            'parent': '.'.join(parent_path.split('.')[:-1]),
            'name': parent_path.split('.')[-1],
            'type': attr_type,
            'description': description
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
                st.table(parameters)
                request_body = get_request_body(method_details.get('requestBody'), spec)
                st.table(request_body)
                # response = get_response()
                excel=write_to_excel(parameters, request_body)

    return excel