import streamlit as st
import yaml
import json

VALID_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace', 'connect'}
COMPONENTS = {}

def parse_openapi_spec(file):
    spec = None
    if file.name.endswith('.yaml') or file.name.endswith('.yml'):
        spec = yaml.safe_load(file)
    elif file.name.endswith('.json'):
        spec = json.load(file)
    return spec


# Function to resolve references ($ref) from the components section, recursively
def resolve_ref(ref):
    global COMPONENTS
    ref_path = ref.split('/')  # e.g., "#/components/schemas/User"
    component_type, component_name = ref_path[2], ref_path[3]
    # Get the referenced schema
    schema = COMPONENTS.get(component_type, {}).get(component_name, {})

    # If the schema itself has a $ref, recursively resolve it
    if '$ref' in schema:
        return resolve_ref(schema['$ref'])

    return schema

# Function to extract details from a schema (whether inline or reusable)
def extract_schema_details(schema):

    properties = schema.get('properties', {})
    required_fields = schema.get('required', [])

    extracted_data = []
    for prop_name, prop_details in properties.items():
        # If the property is itself a reusable component, resolve it

        if '$ref' in prop_details:
            prop_details = resolve_ref(prop_details['$ref'])

        description = prop_details.get('description', 'No description')
        datatype = prop_details.get('type', 'Unknown')
        is_required = prop_name in required_fields
        extracted_data.append({
            'attribute': prop_name,
            'description': description,
            'datatype': datatype,
            'required': is_required
        })

    return extracted_data

def breakdown_schema(schema):
    if '$ref' in schema:
        ref = schema['$ref']
        resolved_schema = resolve_ref(ref)
        extract_schema_details(resolved_schema)
    else:
        # Inline schema
        extract_schema_details(schema)

def breakdown_request_body(request_body):
    request_body_data = []
    if request_body:
        request_body_description = request_body.get('description')
        request_body_content = request_body.get('content')
        if 'application/json' in request_body_content:
            breakdown_schema(request_body_content['application/json'].get('schema', {}))

def breakdown_parameters(parameters):
    if parameters:
        for parameter in parameters:
            parameter_type = parameter.get('in')
            parameter_name = parameter.get('name')
            parameter_required = parameter.get('required')
            parameter_schema = parameter.get('schema')
            parameter_data_type = parameter_schema.get('type')
            parameter_description = parameter_schema.get('description')

def breakdown_methods(methods):
    for method, method_details in methods:
        if method in VALID_METHODS:
            method_description = method_details.get('description', 'Description not provided')
            # parameters
            breakdown_parameters(method_details.get('parameters'))
            breakdown_request_body(method_details.get('requestBody'))

def breakdown_paths(paths):
    for path, path_details in paths.items():
        path_description = path_details.get('description', 'Description not provided')
        breakdown_methods(path_details.items())

def breakdown_spec(spec):
    #info
    global COMPONENTS
    COMPONENTS = spec.get('components', {})  # extract re-usable components
    breakdown_paths(spec.get('paths', {}))


def convert_spec_to_excel(file):
    excel = breakdown_spec(parse_openapi_spec(file))