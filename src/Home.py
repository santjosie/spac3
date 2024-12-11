import streamlit as st


def main():
    st.set_page_config(
        page_title='spac3 | Home',
        page_icon=':twisted_rightwards_arrows:',
        layout='wide',
        menu_items={
            'Get help': 'https://www.santhoshjose.dev',
            'Report a bug': 'https://github.com/santjosie/spac3/issues',
            'About': '# Version: 2.2 #'
        })
    st.header("Spac3!")
    st.caption("OpenAPI spec management platform")

def navigator():
    pages = {"":
        [st.Page("Home.py", title="Home")],
             "Excelsior":
             [st.Page(page="pg/pg_excelsior.py", title="Convert to Excel"),
              st.Page(page="pg/pg_descoder.py", title="Convert to OpenAPI"),
              st.Page(page="pg/pg_sandbox.py", title="Sandbox")],
    }

    pg = st.navigation(pages=pages, expanded=True)
    pg.run()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
    navigator()