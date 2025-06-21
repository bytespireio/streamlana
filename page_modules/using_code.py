import streamlit as st
import yaml


def render():
    st.write(
        "Sometimes we need to render something very custom which might not be possible via configuration."
    )
    st.write(
        "We can still write code(traditional streamlit coding) and integrate into 🐙StreamLana."
    )

    with st.expander("The Config for this page is defined as follows", expanded=False):
        yaml = """  
        side_bar:
          - heading: "Demo Using Code Definition"
            pages:
              - name: "Sometimes code is needed"
                code_definition: "page_modules/using_code.py"
        """
        st.code(yaml, language="yaml")
        st.markdown(
            "refer [github](https://github.com/bytespireio/streamlana/blob/main/demo_side_bar.yaml)"
        )


render()
