from typing import Dict

# Hard-coded Pagination schema definition
PAGINATION_SCHEMA = {
    "Pagination": {
        "type": "object",
        "description": "Pagination details.",
        "properties": {
            "CurrentPage": {
                "type": "integer",
                "description": "Current page number.",
                "example": 1
            },
            "PageSize": {
                "type": "integer",
                "description": "Number of records per page.",
                "example": 10
            },
            "NextPage": {
                "type": "integer",
                "description": "Next page number.",
                "example": 2
            },
            "TotalRecords": {
                "type": "integer",
                "description": "Total number of records.",
                "example": 100
            },
            "TotalPages": {
                "type": "integer",
                "description": "Total number of pages.",
                "example": 10
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
                    "example": "ITRVL_CRUISE_AVAIL_SYS_00001"
                },
                "Message": {
                    "type": "string",
                    "description": "Message returned while processing the request.",
                    "example": "There are no cruises matching the search criteria. Please try modifying the search."
                }
            }
        }
    }
}

NEW_HEADER_PARAMETERS = [
          {
            "name": "x-agency-code",
            "in": "header",
            "description": "Unique identifier for the agency.",
            "required": False,
            "schema": {
              "type": "string",
              "examples": [
                "AVALON"
              ]
            }
          },
          {
            "name": "x-agency-phone",
            "in": "header",
            "description": "Unique phone number of the agency for identifying the agency.",
            "required": False,
            "schema": {
              "type": "string",
              "examples": [
                "9876543210"
              ]
            }
          },
          {
            "name": "x-sub-agency-code",
            "in": "header",
            "description": "Unique identifier of the secondary or sub-agency.",
            "required": False,
            "schema": {
              "type": "string",
              "examples": [
                "AVALON5"
              ]
            }
          },
          {
            "name": "x-sub-agency-phone",
            "in": "header",
            "description": "Unique phone number for identifying the sub-agency.",
            "required": False,
            "schema": {
              "type": "string",
              "examples": [
                "9876543210"
              ]
            }
          },
          {
            "name": "x-brand",
            "in": "header",
            "description": "Identifies the brand of the cruise line.",
            "required": False,
            "schema": {
              "type": "string",
              "examples": [
                "Vista"
              ]
            }
          },
          {
            "name": "x-market",
            "in": "header",
            "description": "Overrides the default market of the user.",
            "required": False,
            "schema": {
              "type": "string",
              "examples": [
                "EUR"
              ]
            }
          },
          {
            "name": "x-currency",
            "in": "header",
            "description": "Overrides the default currency of the user.",
            "required": False,
            "schema": {
              "type": "string",
              "examples": [
                "USD"
              ]
            }
          },
          {
            "name": "x-userid-token",
            "in": "header",
            "description": "ID token passed in the header for identifying user context.",
            "required": False,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "x-ext-trace-id",
            "in": "header",
            "description": "External transaction id for an API request . Used for end to end traceability.",
            "required": False,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "x-ext-session-id",
            "in": "header",
            "description": "External user session id. Used for locking entities such as bookings.",
            "required": False,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "x-pcc",
            "in": "header",
            "description": "Unique PCC for identifying the agency.",
            "required": False,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "x-office-id",
            "in": "header",
            "description": "Unique identifier for the agency office.",
            "required": False,
            "schema": {
              "type": "string"
            }
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
                            "example": "SYS_005"
                        },
                        "Message": {
                            "type": "string",
                            "description": "Error message.",
                            "example": "System Error Occurred"
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
                            "example": "f2d39f5f5e432f4dd34520d63923808c-2131397101"
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
            if method in ['get', 'post', 'put', 'delete', 'patch']:
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
            if method in ['get', 'post', 'put', 'delete', 'patch']:
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

def process_header(spec, header_content):
    # Remove all header parameters
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            if 'parameters' in details:
                details['parameters'] = [param for param in details['parameters'] if param.get('in') != 'header']
    if header_content == "":
        header_content = NEW_HEADER_PARAMETERS
    # Add new header parameters
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                if 'parameters' not in details:
                    details['parameters'] = []
                details['parameters'].extend(header_content)

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
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                if 'responses' not in details:
                    details['responses'] = {}
                for status_code in ['422', '500']:
                    #if status_code not in details['responses']:
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

    def convert_refs(spec: Dict, old_name: str, new_name: str):
        """
        Recursively search for '$ref' keys in the data structure
        and convert their values to lowercase.
        """
        if isinstance(spec, dict):
            for key, value in spec.items():
                if key == "$ref" and isinstance(value, str) and value.endswith(f"/{old_name}"):
                    spec[key] = value.replace(f"/{old_name}", f"/{new_name}")
                else:
                    convert_refs(value, old_name, new_name)
        elif isinstance(spec, list):
            for item in spec:
                convert_refs(item, old_name, new_name)

    components = openapi_spec['components']

    if components and 'schemas' in components:
        updated_schemas = {}
        for key, value in components['schemas'].items():
            new_key = camel_to_pascal_case(key)
            updated_schemas[new_key] = process_schema(value)
            convert_refs(openapi_spec, key, new_key)
            convert_refs(updated_schemas, key, new_key)
        components['schemas'] = updated_schemas

    if components:
        openapi_spec['components'] = components

    return openapi_spec
