import streamlit as st


def render():
    st.write(
        "Sometimes we need to render something very custom which might not be possible via configuration."  # noqa: E501
    )
    st.write(
        "We can still write code(traditional streamlit coding) and integrate into 🐙StreamLana."  # noqa: E501
    )

    with st.expander("The Config for this page is defined as follows", expanded=False):
        yml = """
        side_bar:
          - heading: "Demo Using Code Definition"
            pages:
              - name: "Sometimes code is needed"
                code_definition: "page_modules/using_code.py"
        """
        st.code(yml, language="yaml")
        st.markdown(
            "refer [github](https://github.com/bytespireio/streamlana/blob/main/demo_side_bar.yaml)"  # noqa: E501
        )


render()
