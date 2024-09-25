from pickle import GLOBAL

import streamlit as st
import pandas as pd
import numpy as np
import yaml
import json
import io
import copy

DESCRIPTIONS_COUNT = 0
UPDATES_TABLE =[]

def resolve_ref(ref, spec):
    """
    Resolve a JSON Reference ($ref) within the OpenAPI specification.
    """
    ref_path = ref.lstrip('#/').split('/')
    result = spec
    for part in ref_path:
        result = result.get(part, {})
    return result

def update_descriptions(schema, spec, path, description_map, visited_refs=None):
    """
    Recursively update descriptions in the schema based on the description_map.
    """
    global DESCRIPTIONS_COUNT
    global UPDATES_TABLE
    if visited_refs is None:
        visited_refs = set()
    if '$ref' in schema:
        ref = schema['$ref']
        if ref in visited_refs:
            return  # Avoid infinite recursion
        visited_refs.add(ref)
        resolved_schema = resolve_ref(ref, spec)
        update_descriptions(resolved_schema, spec, path, description_map, visited_refs)
        return
    if 'allOf' in schema:
        for subschema in schema['allOf']:
            update_descriptions(subschema, spec, path, description_map, visited_refs)
    elif 'anyOf' in schema:
        for subschema in schema['anyOf']:
            update_descriptions(subschema, spec, path, description_map, visited_refs)
    elif 'oneOf' in schema:
        for subschema in schema['oneOf']:
            update_descriptions(subschema, spec, path, description_map, visited_refs)
    elif schema.get('type') == 'object':
        properties = schema.get('properties', {})
        for prop_name, prop_schema in properties.items():
            full_path = f"{path}.{prop_name}" if path else prop_name
            # Update description if present in the map
            if full_path in description_map:
                #had a description that has been removed or updated
                if 'description' in prop_schema and prop_schema['description'] != description_map[full_path]:
                    UPDATES_TABLE.append({'name': prop_name
                                          ,'old_description':prop_schema['description']
                                          ,'new_description':description_map[full_path]})
                    prop_schema['description'] = description_map[full_path]
                    DESCRIPTIONS_COUNT = DESCRIPTIONS_COUNT + 1
                if 'description' not in prop_schema and description_map[full_path] and description_map[full_path] is not None:
                    UPDATES_TABLE.append({'name': prop_name
                                             , 'old_description': None
                                             , 'new_description': description_map[full_path]})
                    prop_schema['description'] = description_map[full_path]
                    DESCRIPTIONS_COUNT = DESCRIPTIONS_COUNT + 1
            update_descriptions(prop_schema, spec, full_path, description_map, visited_refs.copy())
    elif schema.get('type') == 'array':
        items_schema = schema.get('items', {})
        update_descriptions(items_schema, spec, path, description_map, visited_refs.copy())
    else:
        # For primitive types
        if path in description_map:
            if 'description' in schema and schema['description'] != description_map[path]:
                UPDATES_TABLE.append({'name': path
                                         , 'old_description': schema['description']
                                         , 'new_description': description_map[path]})
                schema['description'] = description_map[path]
                DESCRIPTIONS_COUNT = DESCRIPTIONS_COUNT + 1

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

def descode(excel_file, spec_file):
    global DESCRIPTIONS_COUNT
    global UPDATES_TABLE
    DESCRIPTIONS_COUNT = 0
    UPDATES_TABLE =[]
    # Read Excel file into DataFrame
    df_attributes = pd.read_excel(excel_file, sheet_name='attributes')
    df_attributes = df_attributes.replace({np.nan: None})
    # Ensure required columns are present
    required_columns = ['full_path', 'name', 'description']
    if not all(col in df_attributes.columns for col in required_columns):
        st.error(f"Excel file must contain columns: {', '.join(required_columns)}")
        return

    description_map = pd.Series(df_attributes['description'].values, index=df_attributes['full_path']).to_dict()
    st.write(description_map)
    spec = load_oapi_spec(spec_file)

    # deep copy of spec to avoid modifying the original
    updated_spec = copy.deepcopy(spec)

    # Update descriptions in the spec
    components = updated_spec.get('components', {})
    schemas = components.get('schemas', {})
    for schema_name, schema in schemas.items():
        schema_path = schema_name  # Top-level schema name
        update_descriptions(schema, updated_spec, schema_path, description_map)

    # Output the updated spec
    st.success(str(DESCRIPTIONS_COUNT) + " descriptions updated!")
    st.subheader('List of changes')
    st.table(UPDATES_TABLE)

    # Provide a download link for the updated spec
    updated_spec_str = yaml.dump(updated_spec, sort_keys=False)

    return updated_spec_str

