import streamlit as st
import pandas as pd
import numpy as np
import copy
import yaml
from .file_handler import load_oapi_spec, write_to_excel
import ast

VALID_METHODS = {'get', 'post'} #, 'put', 'patch', 'delete', 'head', 'options', 'trace', 'connect'}
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

def append_attribute(full_path, name, type, description, example, examples, format, enum, attributes):
    attributes.append({
        'full_path': full_path,
        'name': name,
        'type': type,
        'format': format,
        'description': description,
        'example': example,
        'examples': examples,
        'enum': enum
    })
    return attributes

def update_descriptions(full_path, schema, new_row):
    global UPDATES_TABLE
    if 'description' in schema and schema['description'] != new_row[0]:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'description'
                                 , 'old_value': schema['description']
                                 , 'new_value': new_row[0]})
        if new_row[0] is None:
            del schema['description']
        else:
            schema['description'] = new_row[0]
        # new description addition
    if 'description' not in schema and new_row[0] is not None:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'description'
                                 , 'old_value': None
                                 , 'new_value': new_row[0]})
        schema['description'] = new_row[0]

    #type
    if 'type' in schema and schema['type'] != new_row[1]:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'type'
                                 , 'old_value': schema['type']
                                 , 'new_value': new_row[1]})
        if new_row[1] is None:
            del schema['type']
        else:
            schema['type'] = new_row[1]

        # new type addition
    if 'type' not in schema and new_row[1] is not None:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'type'
                                 , 'old_value': None
                                 , 'new_value': new_row[1]})
        schema['type'] = new_row[1]

    #format
    if 'format' in schema and schema['format'] != new_row[2]:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'format'
                                 , 'old_value': schema['format']
                                 , 'new_value': new_row[2]})
        if new_row[2] is None:
            del schema['format']
        else:
            schema['format'] = new_row[2]
        # new format addition
    if 'format' not in schema and new_row[2] is not None:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'format'
                                 , 'old_value': None
                                 , 'new_value': new_row[2]})
        schema['format'] = new_row[2]

    #examples
    if 'examples' in schema and schema['examples'] != new_row[3]:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'examples'
                                 , 'old_value': schema['examples']
                                 , 'new_value': new_row[3]})
        if new_row[3] is None:
            del schema['examples']
        else:
            schema['examples'] = new_row[3]
    if 'examples' not in schema and new_row[3] is not None:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'examples'
                                 , 'old_value': None
                                 , 'new_value': new_row[3]})
        schema['examples'] = new_row[3]

    #enum
    if 'enum' in schema and schema['enum'] != new_row[4]:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'enum'
                                 , 'old_value': schema['enum']
                                 , 'new_value': new_row[4]})
        if new_row[4] is None:
            del schema['enum']
        else:
            schema['enum'] = new_row[4]
        # new enum addition
    if 'enum' not in schema and new_row[4] is not None:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'enum'
                                 , 'old_value': None
                                 , 'new_value': new_row[4]})
        schema['enum'] = new_row[4]

    #example
    if 'example' in schema and schema['example'] != new_row[5]:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'example'
                                 , 'old_value': schema['example']
                                 , 'new_value': new_row[5]})
        if new_row[5] is None:
            del schema['example']
        else:
            schema['example'] = new_row[5]
        # new example addition
    if 'example' not in schema and new_row[5] is not None:
        UPDATES_TABLE.append({'name': full_path
                                 , 'change_type': 'example'
                                 , 'old_value': None
                                 , 'new_value': new_row[5]})
        schema['example'] = new_row[5]

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

    if schema.get('type') == 'object':
        parent_path = f"{parent_path}.{object_name}" if parent_path else object_name
        if mode in ['extract', 'schemas']:
            append_attribute(full_path=parent_path,
                             name=object_name,
                             type=schema.get('type'),
                             description=schema.get('description', ''),
                             example=schema.get('example', ''),
                             examples=schema.get('examples', ''),
                             format=schema.get('format', ''),
                             enum=schema.get('enum', ''),
                             attributes=attributes)
        else:
            if parent_path in description_map:
                update_descriptions(parent_path, schema, description_map[parent_path])

        properties = schema.get('properties', {})
        for prop_name, prop_schema in properties.items():
            attr_type = prop_schema.get('type', '$ref')
            if attr_type not in ['object', 'array', '$ref']:
                full_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
                # Append attributes
                if mode in ['extract', 'schemas']:
                    append_attribute(full_path=full_path,
                                     name=prop_name,
                                     type=attr_type,
                                     description=prop_schema.get('description', ''),
                                     example=prop_schema.get('example', ''),
                                     examples=prop_schema.get('examples', ''),
                                     format=prop_schema.get('format', ''),
                                     enum=prop_schema.get('enum', ''),
                                     attributes=attributes)
                else:
                    if full_path in description_map:
                        update_descriptions(full_path, prop_schema, description_map[full_path])
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
            append_attribute(full_path=parent_path,
                             name=object_name,
                             type=schema.get('type'),
                             description=schema.get('description', ''),
                             example=schema.get('example', ''),
                             examples=schema.get('examples', ''),
                             format=schema.get('format',''),
                             enum=schema.get('enum',''),
                             attributes=attributes)
        else:
            if parent_path in description_map:
                update_descriptions(parent_path, schema, description_map[parent_path])

        items_schema = schema.get('items', {})
        #when checking schemas - no need to resolve refs, as they would get picked up later anyway
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
        if item_name == "":
            item_name = object_name
        parent_path = f"{parent_path}.{item_name}" if parent_path else item_name
        if mode in ['extract', 'schemas']:
            append_attribute(full_path=parent_path,
                             name=item_name,
                             type=schema.get('type'),
                             description=schema.get('description'),
                             example=schema.get('example'),
                             examples=schema.get('examples', ''),
                             format=schema.get('format'),
                             enum=schema.get('enum'),
                             attributes=attributes)
        else:
            if parent_path in description_map:
                update_descriptions(parent_path, schema, description_map[parent_path])

    if mode in ['extract', 'schemas']:
        return attributes

def excelsify(file):
    spec = load_oapi_spec(file)
    paths = spec.get('paths', {})

    parameters_status_text = "Processing parameters"
    parameters_status_bar = st.sidebar.progress(value=0, text=parameters_status_text)
    request_body_status_text = "Processing request body"
    request_body_status_bar = st.sidebar.progress(value=0, text=request_body_status_text)
    response_body_status_text = "Processing response body"
    response_body_status_bar = st.sidebar.progress(value=0, text=response_body_status_text)
    schemas_body_status_text = "Processing schemas"
    schemas_body_status_bar = st.sidebar.progress(value=0, text=schemas_body_status_text)

    for path, path_details in paths.items():
        for method, method_details in path_details.items():
            if method in VALID_METHODS:

                # parameters
                parameters = get_parameters(method_details.get('parameters'))
                parameters_status_bar.progress(value=1, text=parameters_status_text)
                """
                with st.expander('Parameters'):
                    st.table(parameters)
                """

                #request body
                request_body = get_req_resp_body(method_details.get('requestBody'), spec, type='request')
                request_body_status_bar.progress(value=1, text=request_body_status_text)
                """
                with st.expander('Request body'):
                    st.table(request_body)
                """

                # response body
                response_body = get_req_resp_body(method_details.get('responses'), spec, type='response')
                response_body_status_bar.progress(value=1, text=response_body_status_text)
                """
                with st.expander('Response body'):
                    st.table(response_body)
                """

    #schemas
    schemas = spec.get('components', {}).get('schemas', {})
    schema_attributes = []
    for schema_name, schema in schemas.items():
        schema_path = schema_name  # Top-level schema name
        schema_attributes.extend(extract_attributes(schema=schema, spec=spec, object_name=schema_path, mode='schemas'))
        schemas_body_status_bar.progress(value=1, text=schemas_body_status_text)
        """
        with st.expander('Schemas'):
            st.table(schema_attributes)
        """
                # response = get_response()
    excel=write_to_excel(parameters, request_body, response_body, schema_attributes)
    parameters_status_bar.empty()
    request_body_status_bar.empty()
    response_body_status_bar.empty()
    schemas_body_status_bar.empty()

    return excel

def convert_string_to_list(string):
    if string:
        return ast.literal_eval(string)
    else:
        return None

def descode(excel_file, spec_file):
    global UPDATES_TABLE
    UPDATES_TABLE =[]
    # Read Excel file into DataFrame
    df_attributes = pd.read_excel(excel_file, sheet_name='schemas')
    df_attributes = df_attributes.replace({np.nan: None})
    # Ensure required columns are present
    required_columns = ['full_path', 'name', 'description', 'type', 'format', 'examples', 'enum']
    if not all(col in df_attributes.columns for col in required_columns):
        st.error(f"Excel file must contain columns: {', '.join(required_columns)}")
        return

    #description_map = pd.Series(df_attributes['description'].values, index=df_attributes['full_path']).to_dict()
    description_map = pd.Series(
        df_attributes.apply(lambda row: (row['description'], row['type'], row['format'], convert_string_to_list(row['examples']), convert_string_to_list(row['enum']), row['example']), axis=1).values,
        index=df_attributes['full_path']).to_dict()
    spec = load_oapi_spec(spec_file)

    # deep copy of spec to avoid modifying the original
    updated_spec = copy.deepcopy(spec)

    # Update descriptions in the spec
    #components = updated_spec.get('components', {})
    schemas = updated_spec.get('components', {}).get('schemas', {})
    for schema_name, schema in schemas.items():
        schema_path = schema_name  # Top-level schema name
        extract_attributes(schema=schema,
                           spec=updated_spec,
                           object_name=schema_path,
                           description_map=description_map,
                           mode='update')

    # Output the updated spec
    st.metric(label="Number of changes", value = len(UPDATES_TABLE))
    st.subheader('List of changes')
    st.table(UPDATES_TABLE)

    # Provide a download link for the updated spec
    updated_spec_str = yaml.dump(updated_spec, sort_keys=False)

    return updated_spec_str