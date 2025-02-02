import streamlit as st
import pandas as pd

LIST_OF_CASES = ["snake_case", "kebab-case", "PascalCase", "camelCase"]
LIST_OF_ERROR_CODES = [401, 402, 403, 404, 422, 500]
LIST_OF_CONTENT_TYPES = ["application/json", "application/xml"]
LIST_OF_PAGINATION_METHODS = ["Page based", "Time based"]


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

def oapi_tab():
    st.text_input("OAPI Version", value="3.1.0")
    st.text_input("API version", value="7.0.0")


def request_tab():
    st.multiselect(label="Choose content types to support in the request body",
                   options=LIST_OF_CONTENT_TYPES,
                   default=["application/json"])
    st.write("Add the list of common parameters")
    df = pd.DataFrame(
        [
            {"name": "x-pcc", "type": "string", "description": True, "example": "application/json"},
            {"name": "x-country-code", "type": "string", "description": False, "example": "hello"},
            {"name": "x-another-one", "type": "string", "description": True, "example": "what"},
        ]
    )
    edited_df = st.data_editor(df, num_rows="dynamic")

def response_tab():
    st.multiselect(label="Choose content types to support in the response",
                   options=LIST_OF_CONTENT_TYPES,
                   default=["application/json"])
    st.multiselect(label="Choose the error response codes to include in the documentation",
                   options=LIST_OF_ERROR_CODES, default=[422, 500])
    err_inp_c, err_disp_c = st.columns(2)
    with err_inp_c:
        st.code(body=ERROR_RESPONSE_SCHEMA,
                language="json",
                wrap_lines=True)
    with err_disp_c:
        st.json(ERROR_RESPONSE_SCHEMA)

def schemas_tab():
    st.radio(label="What casing should all the schema names and attributes use?",
             options=LIST_OF_CASES,
             index=2,
             horizontal=True)

def page_tab():
    st.subheader("Page based")
    st.radio(label="Choose pagination type",
                 options=LIST_OF_PAGINATION_METHODS,
                 index=0)
    st.subheader("Time based")
    
def body():
    st.caption("Define the standards that all your OpenAPI documents should follow")
    oapi_t, request_t, response_t, schemas_t, page_t = st.tabs(["OAPI Document", "Request", "Response", "Schemas", "Pagination"])
    with oapi_t:
        oapi_tab()

    with request_t:
        request_tab()

    with response_t:
        response_tab()

    with schemas_t:
        schemas_tab()

    with page_t:
        page_tab()


body()