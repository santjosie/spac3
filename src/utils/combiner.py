from . import file_handler

def merge_specs(spec_files):
    combined_spec = file_handler.load_oapi_spec(spec_files[0])

    for spec_file in spec_files[1:]:
        spec_data = file_handler.load_oapi_spec(spec_file)
        combined_spec['paths'].update(spec_data.get('paths', {}))
        for component_type, components in spec_data.get('components', {}).items():
            combined_spec['components'][component_type].update(components)

    return combined_spec