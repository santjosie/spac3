import pandas as pd
import io

def write_to_excel(parameters, attributes):
    df_parameters = pd.DataFrame(parameters)
    df_attributes = pd.DataFrame(attributes)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_parameters.to_excel(writer, sheet_name='parameters', index=False)
        df_attributes.to_excel(writer, sheet_name='attributes', index=False)

    output.seek(0)

    return output