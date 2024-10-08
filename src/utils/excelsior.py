import streamlit as st
import pandas as pd
import numpy as np
import copy
import yaml
from .file_handler import load_oapi_spec, write_to_excel

VALID_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace', 'connect'}
UPDATES_TABLE =[]

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

def get_req_resp_body(body, spec, type):
    if type == 'request':
        if body:
            body_content = body.get('content')
            if 'application/json' in body_content:
                schema = body_content['application/json'].get('schema', {})
                attributes_table = extract_attributes(schema, spec)
                return attributes_table
    else:
        if body:
            if '200' in body:
                schema = body['200'].get('content').get('application/json').get('schema', {})
                attributes_table = extract_attributes(schema, spec)
                return attributes_table

def resolve_ref(ref, spec):
    """
    Resolve a JSON Reference ($ref) within the OpenAPI specification.
    """
    ref_path = ref.lstrip('#/').split('/')
    result = spec
    for part in ref_path:
        result = result.get(part, {})
    return result, ref_path[-1]

def append_attribute(full_path, name, type, description, attributes):
    attributes.append({
        'full_path': full_path,
        'name': name,
        'type': type,
        'description': description
    })
    return attributes

def update_descriptions(full_path, schema, new_description):
    global UPDATES_TABLE
    if 'description' in schema and schema['description'] != new_description:
        UPDATES_TABLE.append({'name': full_path
                                 , 'old_description': schema['description']
                                 , 'new_description': new_description})
        # new description addition
    if 'description' not in schema and new_description is not None:
        UPDATES_TABLE.append({'name': full_path
                                 , 'old_description': None
                                 , 'new_description': new_description})

def extract_attributes(schema, spec, parent_path='', visited_refs=None, attributes=None, object_name=None, mode='extract', description_map=None):
    """
    Recursively extract attributes from the schema.
    """
    if mode=='update' and description_map is None:
        st.error('Description map not generated for extract operation')
        return

    if visited_refs is None:
        visited_refs = []
    if (mode=='extract' or mode=='schemas') and attributes is None:
        attributes = []

    # Check if the schema has a $ref to a reusable component
    if mode != 'schemas':
        if '$ref' in schema:
            ref = schema['$ref']
            if ref in visited_refs:
                return attributes  # Avoid infinite recursion
            visited_refs.append(ref)
            resolved_schema, schema_name = resolve_ref(ref, spec)
            return extract_attributes(resolved_schema, spec, parent_path, visited_refs, attributes, schema_name, mode, description_map)

    if 'allOf' in schema:
        for subschema in schema['allOf']:
            extract_attributes(subschema, spec, parent_path, visited_refs, attributes, mode=mode, description_map=description_map)
    elif 'anyOf' in schema:
        for subschema in schema['anyOf']:
            extract_attributes(subschema, spec, parent_path, visited_refs, attributes, mode=mode, description_map=description_map)
    elif 'oneOf' in schema:
        for subschema in schema['oneOf']:
            extract_attributes(subschema, spec, parent_path, visited_refs, attributes, mode=mode, description_map=description_map)    

    elif schema.get('type') == 'object':
        parent_path = f"{parent_path}.{object_name}" if parent_path else object_name
        if mode in ['extract', 'schemas']:
            append_attribute(parent_path, object_name, schema.get('type'), schema.get('description'), attributes)
        else:
            if parent_path in description_map:
                update_descriptions(parent_path, schema, description_map[parent_path])
                schema['description'] = description_map[parent_path]
        properties = schema.get('properties', {})
        for prop_name, prop_schema in properties.items():
            attr_type = prop_schema.get('type', '$ref')
            if attr_type not in ['object', 'array', '$ref']:
                full_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
                # Append attributes
                if mode in ['extract', 'schemas']:
                    append_attribute(full_path, prop_name, attr_type, prop_schema.get('description', ''),attributes)
                else:
                    if full_path in description_map:
                        update_descriptions(full_path, prop_schema, description_map[full_path])
                        prop_schema['description'] = description_map[full_path]
            # Recursively process if it's an object or array
            if attr_type == '$ref':
                if mode=='schemas':
                    pass
                else:
                    extract_attributes(schema=prop_schema,
                                       spec=spec,
                                       parent_path=parent_path,
                                       visited_refs=visited_refs.copy(),
                                       attributes=attributes,
                                       object_name=prop_name,
                                       mode=mode,
                                       description_map=description_map)
            if attr_type in ['object', 'array']:
                extract_attributes(schema=prop_schema,
                                       spec=spec,
                                       parent_path=parent_path,
                                       visited_refs=visited_refs.copy(),
                                       attributes=attributes,
                                       object_name=prop_name,
                                       mode=mode,
                                       description_map=description_map)
    elif schema.get('type') == 'array':
        parent_path = f"{parent_path}.{object_name}" if parent_path else object_name
        if mode in ['extract', 'schemas']:
            append_attribute(parent_path, object_name, schema.get('type'), schema.get('description'), attributes)
        else:
            if parent_path in description_map:
                update_descriptions(parent_path, schema, description_map[parent_path])
                schema['description'] = description_map[parent_path]
        items_schema = schema.get('items', {})
        if '$ref' in items_schema and mode=='schemas':
            pass
        else:
            extract_attributes(schema=items_schema,
                                   spec=spec,
                                   parent_path=parent_path,
                                   visited_refs=visited_refs.copy(),
                                   attributes=attributes,
                                   object_name=object_name,
                                   mode=mode,
                                   description_map=description_map)
    else:
        # Append attributes for native data types
        item_name = schema.get('title', '')
        parent_path = f"{parent_path}.{item_name}" if parent_path else item_name
        if mode in ['extract', 'schemas']:
            append_attribute(parent_path, item_name, schema.get('type'), schema.get('description'), attributes)
        else:
            if parent_path in description_map:
                update_descriptions(parent_path, schema, description_map[parent_path])
                schema['description'] = description_map[parent_path]

    if mode in ['extract', 'schemas']:
        return attributes

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

                #request body
                request_body = get_req_resp_body(method_details.get('requestBody'), spec, type='request')
                with st.expander('Request body'):
                    st.table(request_body)

                #response body
                response_body = get_req_resp_body(method_details.get('responses'), spec, type='response')
                with st.expander('Response body'):
                    st.table(response_body)

                #schemas
                schemas = spec.get('components', {}).get('schemas', {})
                schema_attributes = []
                for schema_name, schema in schemas.items():
                    schema_path = schema_name  # Top-level schema name
                    schema_attributes.extend(extract_attributes(schema=schema, spec=spec, object_name=schema_path, mode='schemas'))
                    #st.write(schema_attributes)
                with st.expander('Schemas'):
                    st.table(schema_attributes)

                # response = get_response()
                excel=write_to_excel(parameters, request_body, response_body, schema_attributes)

    return excel

def descode(excel_file, spec_file):
    global UPDATES_TABLE
    UPDATES_TABLE =[]
    # Read Excel file into DataFrame
    df_attributes = pd.read_excel(excel_file, sheet_name='schemas')
    df_attributes = df_attributes.replace({np.nan: None})
    # Ensure required columns are present
    required_columns = ['full_path', 'name', 'description']
    if not all(col in df_attributes.columns for col in required_columns):
        st.error(f"Excel file must contain columns: {', '.join(required_columns)}")
        return

    description_map = pd.Series(df_attributes['description'].values, index=df_attributes['full_path']).to_dict()
    spec = load_oapi_spec(spec_file)

    # deep copy of spec to avoid modifying the original
    updated_spec = copy.deepcopy(spec)

    # Update descriptions in the spec
    components = updated_spec.get('components', {})
    schemas = components.get('schemas', {})
    for schema_name, schema in schemas.items():
        schema_path = schema_name  # Top-level schema name
        extract_attributes(schema=schema,
                           spec=updated_spec,
                           object_name=schema_path,
                           description_map=description_map,
                           mode='update')

    # Output the updated spec
    st.subheader('List of changes')
    st.table(UPDATES_TABLE)

    # Provide a download link for the updated spec
    updated_spec_str = yaml.dump(updated_spec, sort_keys=False)

    return updated_spec_str