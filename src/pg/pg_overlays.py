import streamlit as st
import yaml
import copy

def deep_get(data, path_parts):
    for part in path_parts:
        if part not in data:
            return None
        data = data[part]
    return data

def deep_set(data, path_parts, value):
    for part in path_parts[:-1]:
        data = data.setdefault(part, {})
    data[path_parts[-1]] = value

def deep_delete(data, path_parts):
    for part in path_parts[:-1]:
        if part not in data:
            return
        data = data[part]
    data.pop(path_parts[-1], None)

def parse_json_pointer(pointer):
    return [part.replace('~1', '/').replace('~0', '~') for part in pointer.lstrip('#/').split('/')]

def body():
    col_base, col_overlay = st.columns(spec=2)
    with col_base:
        base_file = st.file_uploader("📄 Upload your base OpenAPI YAML file", type=["yaml", "yml"])

    with col_overlay:
        overlay_file = st.file_uploader("🧩 Upload your overlay YAML file", type=["yaml", "yml"])

    if base_file and overlay_file:
        base_spec = yaml.safe_load(base_file)
        overlay_spec = yaml.safe_load(overlay_file)

        updated_spec = copy.deepcopy(base_spec)

        if 'actions' not in overlay_spec:
            st.error("❌ Overlay file must contain an 'actions' list.")
        else:
            for action in overlay_spec['actions']:
                target_path = parse_json_pointer(action['target'])
                if action.get('action') == 'remove':
                    deep_delete(updated_spec, target_path)
                    st.info(f"Removed: {action['target']}")
                else:
                    deep_set(updated_spec, target_path, action['value'])
                    st.success(f"Updated: {action['target']}")

            st.subheader("📤 Modified OpenAPI Spec")
            modified_yaml = yaml.dump(updated_spec, sort_keys=False, allow_unicode=True)
            st.code(modified_yaml, language="yaml")

            st.download_button(
                label="⬇️ Download Modified OpenAPI YAML",
                data=modified_yaml,
                file_name=base_file.name,
                mime="text/yaml"
            )

body()