# <img src="readmeLogo.png"/> StreamLana

'*Business Intelligence as Configuration*' 🚀

## Motivation
Think of Streamlit in Grafana style...

Build your BI dashboards with ease, using simple configuration files.

## Demo App

Its deployed live at https://streamlana.streamlit.app/

## Lets do this

1. Install streamlana
```bash
pip install streamlana
```

2. Define your pages in **`hello.yaml`**
```yaml
#hello.yaml
side_bar:
  - heading: "Hello StreamLana"
    pages:
      - name: "Stats page"
        enabled: True
        config_file_path: "page_configs_demo/hello.json"
      - name: "About page"
        config_file_path:  "page_configs_demo/about.json"
        enabled: True
```
3. Lets define page1 layout - number or rows, the widgets in each row, query powering the widget, widget settings.

Lets do 1 row with 2 widgets in it -> **`page_configs_demo/hello.json`**
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

Lets keep this simple 1 widget and 1 row -> **`page_configs_demo/about.json`** 
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
5. Few lines of code for the main app ->  **`hello.py`**
```python
# hello.py
import logging
import duckdb
from streamlana import side_bar_util
from streamlana.side_bar_util import load_side_bar_config_yaml, render_side_bar_pages

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


```

6. Run the app
```bash
streamlit run hello.py
```

## Widget Library

Currently, we support the following widgets:
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

