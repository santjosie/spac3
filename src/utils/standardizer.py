from typing import Dict, List
import yaml

# Hard-coded Pagination schema definition
PAGINATION_SCHEMA = {
    "Pagination": {
        "type": "object",
        "properties": {
            "total": {
                "type": "integer"
            },
            "page": {
                "type": "integer"
            },
            "size": {
                "type": "integer"
            }
        },
        "required": ["total", "page", "size"]
    }
}

# Hard-coded Messages schema definition
MESSAGES_SCHEMA = {
    "Messages": {
        "type": "object",
        "properties": {
            "messages": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": ["messages"]
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

# Hard-coded ErrorResponse schema definition
ERROR_RESPONSE_SCHEMA = {
    "ErrorResponse": {
        "type": "object",
        "properties": {
            "error": {
                "type": "string"
            },
            "message": {
                "type": "string"
            }
        },
        "required": ["error", "message"]
    }
}

def process_pagination(openapi_spec):
    # Load the OpenAPI spec from YAML
    spec = yaml.safe_load(openapi_spec)

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
                                spec['components']['schemas'][schema_name]['properties']['pagination'] = {
                                    "$ref": "#/components/schemas/Pagination"
                                }

    # Dump the updated spec back to YAML
    return yaml.dump(spec)


def process_messages(openapi_spec):
    # Load the OpenAPI spec from YAML
    spec = yaml.safe_load(openapi_spec)

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
                                spec['components']['schemas'][schema_name]['properties']['messages'] = {
                                    "$ref": "#/components/schemas/Messages"
                                }

    # Dump the updated spec back to YAML
    return yaml.dump(spec)

def process_header(openapi_spec):
    # Load the OpenAPI spec from YAML
    spec = yaml.safe_load(openapi_spec)

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

    # Dump the updated spec back to YAML
    return yaml.dump(spec)

def process_error_response(openapi_spec):
    # Load the OpenAPI spec from YAML
    spec = yaml.safe_load(openapi_spec)

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
    return yaml.dump(spec)

def check_and_convert_casing(openapi_spec: Dict) -> Dict:

    def to_pascal_case(name: str) -> str:
        """Converts a string to PascalCase."""
        return name[0].upper() + name[1:]

    def process_schema(schema: Dict) -> Dict:
        """Processes a single schema to check and convert casing."""
        if 'properties' in schema:
            schema['properties'] = {
                to_pascal_case(key): process_properties(value)
                for key, value in schema['properties'].items()
            }
        return schema

    def process_properties(properties: Dict) -> Dict:
        """Processes properties within a schema."""
        if 'type' in properties and properties['type'] == 'object':
            properties = process_schema(properties)
        return properties

    if 'components' in openapi_spec and 'schemas' in openapi_spec['components']:
        openapi_spec['components']['schemas'] = {
            to_pascal_case(key): process_schema(value)
            for key, value in openapi_spec['components']['schemas'].items()
        }

    return openapi_spec