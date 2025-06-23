import os

import streamlit as st


class AppState:
    """Utility class for managing state in Streamlit applications."""

    _hashmap_state_holder = {}

    @classmethod
    def _use_inmem(cls):
        return os.environ.get("STREAMLANA_USE_APP_INMEM_STATE", "").lower() in (
            "1",
            "true",
            "yes",
        )

    @classmethod
    def put(cls, key, value):
        if cls._use_inmem() or st is None:
            cls._hashmap_state_holder[key] = value
        else:
            st.session_state[key] = value

    @classmethod
    def get(cls, key, default_value=None):
        if cls._use_inmem() or st is None:
            return cls._hashmap_state_holder.get(key)
        return st.session_state.get(key, default_value)

    @classmethod
    def clear(cls, keys=[]):
        if cls._use_inmem() or st is None:
            if keys is None:
                cls._hashmap_state_holder.clear()
            else:
                for key in keys:
                    cls._hashmap_state_holder.pop(key, None)
        else:
            if keys is None:
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
            else:
                for key in keys:
                    if key in st.session_state:
                        del st.session_state[key]
