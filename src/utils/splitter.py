def get_referenced_schemas(schema, used_schemas, components):
    """Recursively find all referenced schemas."""
    if not schema:
        return
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        if ref not in used_schemas:
            used_schemas.add(ref)
            if ref in components.get("schemas", {}):
                get_referenced_schemas(components["schemas"][ref], used_schemas, components)
    elif "items" in schema:
        get_referenced_schemas(schema["items"], used_schemas, components)
    elif "properties" in schema:
        for prop in schema["properties"].values():
            get_referenced_schemas(prop, used_schemas, components)
    elif "allOf" in schema:
        for sub_schema in schema["allOf"]:
            get_referenced_schemas(sub_schema, used_schemas, components)
    elif "anyOf" in schema:
        for sub_schema in schema["anyOf"]:
            get_referenced_schemas(sub_schema, used_schemas, components)
    elif "oneOf" in schema:
        for sub_schema in schema["oneOf"]:
            get_referenced_schemas(sub_schema, used_schemas, components)

def split_openapi_file(spec):
    """Split OpenAPI file into separate files for each path."""
    paths = spec.get("paths", {})
    components = spec.get("components", {})
    split_files = []

    for path, path_item in paths.items():
        new_spec = {
            "openapi": spec["openapi"],
            "info": {
                "title": path_item.get("summary", "Untitled"),
                "description": path_item.get("description", "No description provided"),
                "version": spec["info"]["version"]
            },
            "paths": {path: path_item},
            "components": {"schemas": {}}
        }

        # Identify used schemas
        used_schemas = set()
        for operation in path_item.values():
            if isinstance(operation, dict):
                for content in operation.get("requestBody", {}).get("content", {}).values():
                    get_referenced_schemas(content.get("schema"), used_schemas, components)
                for response in operation.get("responses", {}).values():
                    for content in response.get("content", {}).values():
                        get_referenced_schemas(content.get("schema"), used_schemas, components)

        # Retain only used schemas
        for schema_name in used_schemas:
            if schema_name in components.get("schemas", {}):
                new_spec["components"]["schemas"][schema_name] = components["schemas"][schema_name]

        split_files.append((path, new_spec))

    return split_files