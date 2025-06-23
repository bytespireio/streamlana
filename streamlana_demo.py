import logging
from typing import List

import duckdb
from datasketches import compact_theta_sketch, theta_intersection, theta_union
from duckdb.typing import BLOB, DOUBLE

from streamlana import side_bar_util
from streamlana.side_bar_util import load_side_bar_config_yaml, render_side_bar_pages

# ✅ First thing to do, set page layout of streamlit
side_bar_util.set_page_layout(layout="wide")

# logging level
logging.basicConfig(level=logging.INFO)

# ✅ Load side bar configuration from YAML file
side_bar_config = load_side_bar_config_yaml("demo_side_bar.yaml")

# ✅ Create DuckDB connection
con = duckdb.connect()


def union_sketches(sketches: List):
    """Union multiple theta sketches into one."""
    union = theta_union()
    for sketch in sketches:
        if sketch is None:
            continue
        set_sketch = compact_theta_sketch.deserialize(bytes(sketch))
        union.update(set_sketch)
    return union.get_result().serialize()


def estimate_sketch(sketch):
    """Estimate the size of a theta sketch."""
    if sketch is None:
        return None
    sketch = compact_theta_sketch.deserialize(sketch)
    return sketch.get_estimate() if sketch else None


# register apache thetha sketch functions with DuckDB
con.create_function(
    "union_sketches", union_sketches, [duckdb.list_type(BLOB)], return_type=BLOB
)
con.create_function("estimate_sketch", estimate_sketch, [BLOB], return_type=DOUBLE)

# ✅ Render side bar pages based on the configuration
render_side_bar_pages(side_bar_config, con)
