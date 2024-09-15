import streamlit as st

def main():
    st.set_page_config(
        page_title='spac3 | Home',
        page_icon=':material/home:',
        menu_items={
            'Get help': 'https://www.santhoshjose.dev',
            'About': '# Version: 2.2 #'
        })
    st.header("Welcome to spac3!")
    st.caption("OpenAPI spec management platform")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()