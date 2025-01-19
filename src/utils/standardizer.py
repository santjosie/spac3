from typing import Dict, List
import streamlit as st

# Hard-coded Pagination schema definition
PAGINATION_SCHEMA = {
    "Pagination": {
        "type": "object",
        "description": "Pagination details.",
        "properties": {
            "CurrentPage": {
                "type": "integer",
                "description": "Current page number.",
                "examples": [1]
            },
            "PageSize": {
                "type": "integer",
                "description": "Number of records per page.",
                "examples": [10]
            },
            "NextPage": {
                "type": "integer",
                "description": "Next page number.",
                "examples": [2]
            },
            "TotalRecords": {
                "type": "integer",
                "description": "Total number of records.",
                "examples": [100]
            },
            "TotalPages": {
                "type": "integer",
                "description": "Total number of pages.",
                "examples": [10]
            },
        }
    }
}

MESSAGES_SCHEMA = {
    "Messages": {
        "type": "array",
        "title": "Messages",
        "description": "Messages returned while processing the request.",
        "items": {
            "type": "object",
            "title": "Message",
            "properties": {
                "Code": {
                    "type": "string",
                    "description": "Unique identifier for the message.",
                    "examples": [
                        "ITRVL_CRUISE_AVAIL_SYS_00001"
                    ]
                },
                "Message": {
                    "type": "string",
                    "description": "Message returned while processing the request.",
                    "examples": [
                        "There are no cruises matching the search criteria. Please try modifying the search."
                    ]
                }
            }
        }
    }
}

NEW_HEADER_PARAMETERS = [
    {
        "name": "X-Request-ID",
        "in": "header",
        "required": True,
        "schema": {
            "type": "string"
        },
        "description": "Unique request ID"
    },
    {
        "name": "X-Client-ID",
        "in": "header",
        "required": True,
        "schema": {
            "type": "string"
        },
        "description": "Client ID"
    }
]

ERROR_RESPONSE_SCHEMA = {
    "ErrorResponse": {
        "type": "object",
        "title": "ErrorResponse",
        "description": "Object returned when the API processing fails.",
        "properties": {
            "Errors": {
                "type": "array",
                "title": "Errors",
                "description": "List of errors encountered while processing the request.",
                "items": {
                    "type": "object",
                    "title": "Error",
                    "properties": {
                        "Code": {
                            "type": "string",
                            "description": "Error code.",
                            "examples": [
                                "SYS_005"
                            ]
                        },
                        "Message": {
                            "type": "string",
                            "description": "Error message.",
                            "examples": [
                                "System Error Occurred"
                            ]
                        },
                        "Severity": {
                            "type": "string",
                            "enum": [
                                "ERROR",
                                "WARN",
                                "INFO",
                                "FINE"
                            ],
                            "description": "Severity of the error."
                        },
                        "CorrelationId": {
                            "type": "string",
                            "description": "This is a reference to the transaction id of the error.",
                            "examples": [
                                "f2d39f5f5e432f4dd34520d63923808c-2131397101"
                            ]
                        }
                    }
                }
            }
        }
    }
}

def remove_path_servers(spec):

    # Check for the existence of a node called 'servers' under each path and delete it if it exists
    for path, methods in spec.get('paths', {}).items():
        if 'servers' in methods:
            del methods['servers']

    return spec

def remove_non_json_content(spec):

    # Check for the existence of request body and remove non-application/json content types
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            if 'requestBody' in details:
                content = details['requestBody'].get('content', {})
                for content_type in list(content.keys()):
                    if content_type != 'application/json':
                        del content[content_type]

    # Check for the existence of response bodies and remove non-application/json content types
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            if 'responses' in details:
                for response in details['responses'].values():
                    content = response.get('content', {})
                    for content_type in list(content.keys()):
                        if content_type != 'application/json':
                            del content[content_type]

    return spec

def process_pagination(spec):
    # Load the OpenAPI spec from YAML
    #spec = yaml.safe_load(openapi_spec)

    # Insert the Pagination schema into the components section
    if 'components' not in spec:
        spec['components'] = {}
    if 'schemas' not in spec['components']:
        spec['components']['schemas'] = {}
    spec['components']['schemas']['Pagination'] = PAGINATION_SCHEMA['Pagination']

    # Check for 200 or 201 response codes and update the schema
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            for status_code in ['200', '201']:
                if status_code in details.get('responses', {}):
                    response = details['responses'][status_code]
                    if 'content' in response and 'application/json' in response['content']:
                        schema_ref = response['content']['application/json']['schema'].get('$ref')
                        if schema_ref:
                            schema_name = schema_ref.split('/')[-1]
                            if schema_name in spec['components']['schemas']:
                                spec['components']['schemas'][schema_name]['properties']['Pagination'] = {
                                    "$ref": "#/components/schemas/Pagination"
                                }

    return spec


def process_message(spec):
    # Load the OpenAPI spec from YAML
    #spec = yaml.safe_load(openapi_spec)

    # Insert the Messages schema into the components section
    if 'components' not in spec:
        spec['components'] = {}
    if 'schemas' not in spec['components']:
        spec['components']['schemas'] = {}
    spec['components']['schemas']['Messages'] = MESSAGES_SCHEMA['Messages']

    # Check for 200 or 201 response codes and update the schema
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            for status_code in ['200', '201']:
                if status_code in details.get('responses', {}):
                    response = details['responses'][status_code]
                    if 'content' in response and 'application/json' in response['content']:
                        schema_ref = response['content']['application/json']['schema'].get('$ref')
                        if schema_ref:
                            schema_name = schema_ref.split('/')[-1]
                            if schema_name in spec['components']['schemas']:
                                spec['components']['schemas'][schema_name]['properties']['Messages'] = {
                                    "$ref": "#/components/schemas/Messages"
                                }

    return spec

def process_header(spec):

    # Remove all header parameters
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            if 'parameters' in details:
                details['parameters'] = [param for param in details['parameters'] if param.get('in') != 'header']

    # Add new header parameters
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            if 'parameters' not in details:
                details['parameters'] = []
            details['parameters'].extend(NEW_HEADER_PARAMETERS)

    return spec

def process_error_response(spec):
    # Load the OpenAPI spec from YAML
    #spec = yaml.safe_load(openapi_spec)

    # Check and update/add ErrorResponse schema
    if 'components' not in spec:
        spec['components'] = {}
    if 'schemas' not in spec['components']:
        spec['components']['schemas'] = {}
    spec['components']['schemas']['ErrorResponse'] = ERROR_RESPONSE_SCHEMA['ErrorResponse']

    # Check and update/add error response codes
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            if 'responses' not in details:
                details['responses'] = {}
            for status_code in ['422', '500']:
                if status_code not in details['responses']:
                    details['responses'][status_code] = {
                        "description": "Error response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    }

    # Dump the updated spec back to YAML
    #return yaml.dump(spec)
    return spec

def check_and_convert_casing(openapi_spec):

    def camel_to_pascal_case(name: str) -> str:
        """Converts SnakeCase to PascalCase."""
        return name[0].upper() + name[1:]

    def process_schema(schema: Dict) -> Dict:
        """Processes a single schema to check and convert casing."""
        if 'properties' in schema:
            schema['properties'] = {
                camel_to_pascal_case(key): process_properties(value)
                for key, value in schema['properties'].items()
            }
        return schema

    def process_properties(properties: Dict) -> Dict:
        """Processes properties within a schema."""
        if 'type' in properties and properties['type'] == 'object':
            properties = process_schema(properties)
        return properties

    def update_references(spec: Dict, old_name: str, new_name: str):
        """Updates references to the schema with the new name."""
        for path, methods in spec.get('paths', {}).items():
            for method, details in methods.items():
                if 'requestBody' in details:
                    content = details['requestBody'].get('content', {})
                    for content_type, media_type in content.items():
                        if '$ref' in media_type.get('schema', {}):
                            ref = media_type['schema']['$ref']
                            if ref.endswith(f"/{old_name}"):
                                media_type['schema']['$ref'] = ref.replace(f"/{old_name}", f"/{new_name}")
                if 'responses' in details:
                    for response in details['responses'].values():
                        content = response.get('content', {})
                        for content_type, media_type in content.items():
                            if '$ref' in media_type.get('schema', {}):
                                ref = media_type['schema']['$ref']
                                if ref.endswith(f"/{old_name}"):
                                    media_type['schema']['$ref'] = ref.replace(f"/{old_name}", f"/{new_name}")

                if 'components' in spec and 'schemas' in spec['components']:
                    for schema_name, schema in spec['components']['schemas'].items():
                        if '$ref' in schema.get('properties', {}):
                            ref = schema['properties']['$ref']
                            if ref.endswith(f"/{old_name}"):
                                schema['properties']['$ref'] = ref.replace(f"/{old_name}", f"/{new_name}")

    components = openapi_spec['components']

    if components and 'schemas' in components:
        updated_schemas = {}
        for key, value in components['schemas'].items():
            new_key = camel_to_pascal_case(key)
            updated_schemas[new_key] = process_schema(value)
            update_references(openapi_spec, key, new_key)
        components['schemas'] = updated_schemas

    if components:
        openapi_spec['components'] = components

    return openapi_spec
"""
    if 'components' in openapi_spec and 'schemas' in openapi_spec['components']:
        openapi_spec['components']['schemas'] = {
            camel_to_pascal_case(key): process_schema(value)
            for key, value in openapi_spec['components']['schemas'].items()
        }
"""
