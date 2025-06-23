import streamlit as st

st.title("Check the Url in the Browser.")
col1, col2 = st.columns([0.5, 0.5])
with col1:
    with st.container(height=150, border=True):
        st.image("anon.png", width=800)
with col2:
    st.empty()
yaml = """
side_bar:
  - heading: "Demo"
    pages:
      - name: "Anonymous Page Id"
        anonymous: True
        code_definition: "page_modules/anonymous.py"
"""
st.write("The config is defined as follows:")
st.code(yaml, language="yaml", width=550)
