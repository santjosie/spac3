from .file_handler import load_oapi_spec, write_to_excel
import streamlit as st

def append_attribute(full_path, name, type, description, attributes):
    attributes.append({
        'full_path': full_path,
        'name': name,
        'type': type,
        'description': description
    })
    return attributes

def extract_attributes(schema, spec, parent_path='', visited_refs=None, attributes=None, object_name=None):
    """
    Recursively extract attributes from the schema.
    """

    if visited_refs is None:
        visited_refs = []
    if attributes is None:
        attributes = []

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
        parent_path = f"{parent_path}.{object_name}" if parent_path else object_name
        append_attribute(parent_path, object_name, schema.get('type'), schema.get('description'), attributes)
        properties = schema.get('properties', {})
        for prop_name, prop_schema in properties.items():
            attr_type = prop_schema.get('type', '$ref')
            if attr_type not in ['object', 'array', '$ref']:
                full_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
                append_attribute(full_path, prop_name, attr_type, prop_schema.get('description', ''),attributes)
            # Recursively process if it's an object or array
            if attr_type in ['object', 'array']:
                extract_attributes(schema=prop_schema, spec=spec, parent_path=parent_path, visited_refs=visited_refs.copy(), attributes=attributes, object_name=prop_name)
    elif schema.get('type') == 'array':
        parent_path = f"{parent_path}.{object_name}" if parent_path else object_name
        append_attribute(parent_path, object_name, schema.get('type'), schema.get('description'), attributes)
        items = schema.get('items', {})
    else:
        # Append attributes for native data types
        item_name = schema.get('title', '')
        parent_path = f"{parent_path}.{item_name}" if parent_path else item_name
        append_attribute(parent_path, item_name, schema.get('type'), schema.get('description'), attributes)

    return attributes

def excelsifyer(file):
    spec = load_oapi_spec(file)

    schemas = spec.get('components', {}).get('schemas', {})
    schema_attributes = []

    for schema_name, schema in schemas.items():
        schema_path = schema_name  # Top-level schema name
        schema_attributes.extend(extract_attributes(schema=schema, spec=spec, object_name=schema_path))

        with st.expander('Schemas'):
            st.table(schema_attributes)

        excel=write_to_excel(schema_attributes=schema_attributes)

    return excel