# hello.py
import logging

import duckdb

import side_bar_util
from side_bar_util import load_side_bar_config_yaml, render_side_bar_pages

# ✅ First thing to do, set page layout of streamlit
side_bar_util.set_page_layout(layout="wide")

# logging level
logging.basicConfig(level=logging.INFO)

# ✅ Load side bar configuration from YAML file
side_bar_config = load_side_bar_config_yaml("hello.yaml")

# ✅ Create DuckDB connection (do your setup with it)
con = duckdb.connect()

# ✅ Render side bar pages based on the configuration
render_side_bar_pages(side_bar_config, con)
