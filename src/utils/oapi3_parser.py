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
        return resolve_ref(schema['$ref']), component_name

    return schema, component_name

# Function to extract details from a schema (whether inline or reusable)
def extract_schema_details(schema, component_name):
    st.write(schema)
    properties = schema.get('properties', {})
    schema_datatype = schema.get('type', {})
    schema_description = schema.get('description', {})
    required_fields = schema.get('required', [])

    property_table = []
    for prop_name, prop_details in properties.items():
        # If the property is itself a reusable component, resolve it
        property_description = prop_details.get('description', 'No description')
        property_datatype = prop_details.get('type', 'Unknown')
        is_required = prop_name in required_fields
        property_table.append({
            'Name': component_name+'.'+prop_name,
            'Description': property_description,
            'Datatype': property_datatype,
            'Required': is_required
        })

        while '$ref' in prop_details:
            prop_details, component_name = resolve_ref(prop_details['$ref'])
            property_table.append(extract_schema_details(prop_details, component_name))

    st.table(property_table)
    return property_table

def breakdown_schema(schema):
    if '$ref' in schema:
        ref = schema['$ref']
        resolved_schema, component_name = resolve_ref(ref)
        extracted = extract_schema_details(resolved_schema, component_name)
        st.write(extracted)
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
    parameters_table = []
    if parameters:
        for parameter in parameters:
            parameters_table.append({"Parameter type":parameter.get('in')
                ,"Name":parameter.get('name')
                ,"Required":parameter.get('required')
                ,"Data-type":parameter.get('schema').get('type')
                ,"Description":parameter.get('schema').get('description')})
        st.table(parameters_table)

def breakdown_methods(methods):
    for method, method_details in methods:
        if method in VALID_METHODS:
            method_description = method_details.get('description', 'Description not provided')
            st.subheader(method)
            st.caption(method_description)
            # parameters
            breakdown_parameters(method_details.get('parameters'))
            breakdown_request_body(method_details.get('requestBody'))

def breakdown_paths(paths):
    for path, path_details in paths.items():
        path_description = path_details.get('description', 'Description not provided')
        st.header(path)
        st.caption(path_description)
        breakdown_methods(path_details.items())

def breakdown_spec(spec):
    #info
    global COMPONENTS
    COMPONENTS = spec.get('components', {})  # extract re-usable components
    breakdown_paths(spec.get('paths', {}))


def convert_spec_to_excel(file):
    excel = breakdown_spec(parse_openapi_spec(file))