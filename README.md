# <img src="readmeLogo.png"/> StreamLana

'*Business Intelligence as Configuration*' 🚀

## Motivation
Think of Streamlit in Grafana style...

Build your BI dashboards with ease, using simple configuration files.

![Streamlana Flow](simple_explanation.jpg)

## Live App & Examples:

Its deployed live at https://streamlana.streamlit.app/

For the live app - refer to 'demo' branch of this repo. (refer 'streamlana_demo.py')

## Lets do Hello World app

1. Install streamlana
```bash
pip install streamlana
mkdir page_configs
touch hello_world_app.yaml
touch hello_world_app.py
touch page_configs/stats.json
touch page_configs/about.json
```

2. Define your pages in **`hello_world_app.yaml`**
```yaml
#hello_world_app.yaml
side_bar:
  - heading: "Hello StreamLana"
    pages:
      - name: "Stats page"
        enabled: True
        anonymous: False
        config_file_path: "page_configs/stats.json"
      - name: "About page"
        config_file_path:  "page_configs/about.json"
        enabled: True
        anonymous: False
```
3. Lets define page1 layout - number of rows, the widgets in each row, Query powering the widget, widget settings.

Lets do 1 row with 2 widgets in it -> **`page_configs/stats.json`**
```json
{
    "page_title": "Hello StreamLana",
    "page_rows": [
        {
            "widgets_width_spec": [
                0.4,0.6
            ],
            "widgets_border": true,
            "with_expander": {
                "label": "2 widgets in 1st row, 40/60% width",
                "expanded": true
            },
            "widgets_gap": "small",
            "widgets_vertical_alignment": "top",
            "widgets": [
              {
                    "type": "dataframe",
                    "widget_enabled": true,
                    "query": "SELECT avg_spend,order_date FROM (SELECT order_date, RANDOM() * 1000 AS avg_spend FROM generate_series(CURRENT_DATE - INTERVAL 30 DAY, CURRENT_DATE, INTERVAL 1 DAY) AS t(order_date)) as sub",
                    "config": {
                        "column_order": [
                            "avg_spend",
                            "order_date"
                        ]
                    }
                },
                {
                    "type": "line_chart",
                    "widget_enabled": true,
                    "query": "SELECT avg_spend,order_date FROM (SELECT order_date, RANDOM() * 1000 AS avg_spend FROM generate_series(CURRENT_DATE - INTERVAL 30 DAY, CURRENT_DATE, INTERVAL 1 DAY) AS t(order_date)) as sub",
                    "config": {
                        "x": "order_date",
                        "y": ["avg_spend"],
                        "title": "avgSpend Over Time"
                    }
                }
            ]
        }
    ]
}
```

4. Lets define page2 layout - number or rows, the widgets in each row, query powering the widget, widget settings.

Lets keep this simple 1 widget and 1 row -> **`page_configs/about.json`** 
```json
{
    "page_title": "About StreamLana",
    "page_rows": [
        {
            "widgets_width_spec": [1],
            "widgets": [{"type": "title", "config": {"body": "Business Intelligence as Configuration"}}]
        }
    ]
}
```
5. Few lines of code for the main app ->  **`hello_world_app.py`**
```python
# hello_world_app.py
import logging
import duckdb
from streamlana import side_bar_util
from streamlana.side_bar_util import load_side_bar_config_yaml, render_side_bar_pages

# ✅ First thing to do, set page layout of streamlit
side_bar_util.set_page_layout(layout="wide")

# logging level
logging.basicConfig(level=logging.INFO)

# ✅ Load side bar configuration from YAML file
side_bar_config = load_side_bar_config_yaml("hello_world_app.yaml")

# ✅ Create DuckDB connection (do your setup with it)
con = duckdb.connect()

# ✅ Render side bar pages based on the configuration
try:
    render_side_bar_pages(side_bar_config, con)
finally:
    # ✅ Close the DuckDB connection
    con.close()
    logging.info("DuckDB connection closed.")
```

6. Run the app
```bash
streamlit run hello_world_app.py
```

## Widget Library

Currently, we support the following widgets:
(see examples with their configs in live [demo](https://streamlana.streamlit.app/))

- st.dataframe
- st.line_chart
- st.area_chart
- st.bar_chart
- st.pie_chart
- st.json
- st.title
- st.metric
- st.text
- st.markdown
- st.image
- st.map
- st.empty
- st.selectbox
- st.header

Adding new widgets is easy, just add a new widget type in the `chart_helpers.py`.

ex: implement 'render_<chart_name>(data:pd.DataFrame, config_dict: dict)'

data comes from the duckdb sql query u configure.

## The Design

1. Streamlana supports Multipage app (based on st.navigation).
2. We start off with the side bar configuration file, which defines the pages and their corresponding configuration files. 
3. In the sidebar configuration file, each page can be enabled or disabled, and it can have a title. Optionally it can have anonymous page id. (refer to [demo](https://streamlana.streamlit.app/5ecb7dde))
3. The page configuration file defines the layout of the page.
4. The page layout is defined in terms of rows, each row can have multiple widgets + a page can have optional title.
5. Each row has "widgets_width_spec", which is a list of widths for each widget in the row, summing up to 1.0 (100%) - similar to st.columns 'spec'.
6. Each row can have "widgets_border" to add a border around the widgets in the row. (similar to st.columns with border)
5. Each row can have a Expander (similar to st.expander) to group widgets together in the row, with optional label and expanded state. (Set to null if not needed)
6. Each Row can have a gap between widgets, and vertical alignment of widgets. (similar to st.columns with gap and vertical alignment)
7. Each row has a list of widgets.
8. Each widget has a type, query (duckdb), and configuration. It can be enabled/disabled too.
9. Most of the configuration parameters for a widget are the same as those provided by Streamlit. (see examples in live [demo](https://streamlana.streamlit.app/))