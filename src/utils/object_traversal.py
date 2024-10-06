import yaml
import json
import streamlit as st

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

def create_attribute_table(response_ref, spec):
    """
    Create a table of attributes from the response schema.
    """
    response_schema = resolve_ref(response_ref, spec)
    attributes = extract_attributes(response_schema, spec)
    return attributes

# Load the OpenAPI specification (YAML or JSON)
def load_openapi_spec(file):
    spec = None
    if file.name.endswith('.yaml') or file.name.endswith('.yml'):
        spec = yaml.safe_load(file)
    elif file.name.endswith('.json'):
        spec = json.load(file)
    return spec

# Example usage
if __name__ == "__main__":
    st.set_page_config(
        page_title='spac3 | Home',
        page_icon=':material/home:',
        menu_items={
            'Get help': 'https://www.santhoshjose.dev',
            'About': '# Version: 2.2 #'
        })
    st.header("Welcome to spac3!")
    st.caption("OpenAPI spec management platform")
    uploaded_file = st.file_uploader(label="Upload the open API spec that you want to convert into Excel",
                                     type=["yaml", "yml", "json"], accept_multiple_files=False)
    if uploaded_file:
        response_ref = '#/components/schemas/CruisePromotionRequest'  # Replace with your response object reference

        spec = load_openapi_spec(uploaded_file)
        attribute_table = create_attribute_table(response_ref, spec)
        st.table(attribute_table)
        # Print the attribute table
        print(f"{'Attribute Name':<30} {'Data Type':<15} {'Description':<40} {'Parent':<30}")
        print('-' * 115)
        for attr in attribute_table:
            print(f"{attr['name']:<30} {attr['type']:<15} {attr['description']:<40} {attr['parent']:<30}")


