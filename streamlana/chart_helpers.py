import logging
from datetime import datetime
from typing import Any, Callable, List, Optional, Sequence, Union

import pandas as pd
import streamlit as st

from streamlana.app_state import AppState
from streamlana.util import get_date


def render_rendering_failure(data: str, config_dict=None):
    """
    Render a failure message when a chart fails to render.
    nice name is it not... :)
    :param data: error message
    :param config_dict:
    :return:
    """
    if isinstance(data, str):
        msg = data
    elif isinstance(data, pd.DataFrame):
        if "message" in data.columns:
            msg = data["message"].iloc[0]
        else:
            msg = 'query does not return df with "message" column.'
    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            border: 2px dashed #FFA726;
            border-radius: 10px;
            background-color: #fff8e1;
            text-align: center;
        ">
            <div>
                {msg}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def __render_date_input(
    label: str,
    value: Union[datetime.date, str] = "Date Picker",
    min_value: Optional[datetime.date] = None,
    max_value: Optional[datetime.date] = None,
    help: Optional[str] = None,
    format: str = "YYYY/MM/DD",
    disabled: bool = False,
    label_visibility: str = "visible",
    on_change=None,
    key=None,
):
    """
    Wrapper for st.date_input with all parameters.
    """
    return st.date_input(
        label=label,
        value=value,
        min_value=min_value,
        max_value=max_value,
        help=help,
        format=format,
        disabled=disabled,
        label_visibility=label_visibility,
        on_change=on_change,
        key=key,
    )


def render_date_input(data, config_dict):
    """
    Render a date input using Streamlit's st.date_input with configuration parameters.

    Parameters:
    - data (Any): df consisting of 2 columns containing start_date and end_date respectively.
    The name of the columns should be specified in config_dict with keys 'start_date_column' and 'end_date_column'.
    If data is None or it does not contain the specified columns, the start/end dates displayed will be based on the 'value' key in config_dict.
    - config_dict (dict): Configuration dictionary containing:
        - start_date_column (str): Column name for start date in data (default is 'start_date').This can be used as placeholder in sql query as '__start_date__'
        - end_date_column (str): Column name for end date in data (default is 'end_date'). This can be used as placeholder in sql query as '__end_date__'
        - timezone (str): Timezone to use for date calculations (default is 'UTC').
        - value (str): array of 2 strings, the first is the label for start date and the second is the label for end date. ex: [today-7, today+1] or [today-7, today] or [today]
        - label (str): Label for the date input widget. default: ""
        - min_value (str): Minimum selectable date. accepted formats are 'today', 'today-N' or 'today+N' where N is an integer.
        - max_value (str): Maximum selectable date. accepted formats are 'today', 'today-N' or 'today+N' where N is an integer.
        - help (str): Optional help text.
        - format (str): Date format string. default "YYYY/MM/DD"
        - label_visibility (str): Visibility of the label ('visible', 'hidden', 'collapsed').


    """
    logging.info("Rendering Date input with configuration: %s, %s", None, data)
    start_date_col_name = config_dict.get("start_date_column", "start_date")
    end_date_col_name = config_dict.get("end_date_column", "end_date")
    timezone = config_dict.get("timezone", "UTC")

    if (
        data is not None
        and start_date_col_name in data.columns
        and start_date_col_name in data.columns
    ):
        start_date = data.loc[0, start_date_col_name].date()
        end_date = data.loc[0, end_date_col_name].date()
        date_array = [start_date, end_date]
    else:
        value = config_dict.get("value", None)
        if value is None or len(value) == 0:
            value = "[today-7, today]"
        if len(value) == 1:
            value = [value[0], value[0]]

        date_array = [
            get_date(value[0], zone=timezone),
            get_date(value[1], zone=timezone),
        ]

    configured_min_value = config_dict.get("min_value", "today-365")
    configured_max_value = config_dict.get("max_value", "today+1")
    min_date = get_date(configured_min_value, zone=timezone)
    max_date = get_date(configured_max_value, zone=timezone)
    logging.info(
        "for date_input using min_date: %s, max_date: %s, date_array: %s",
        min_date,
        max_date,
        date_array,
    )

    # AppState.put(start_date_col_name, date_array[0])
    # AppState.put(end_date_col_name, date_array[1])

    displayed_date = __render_date_input(
        label=config_dict.get("label", "Select Date Range"),
        value=date_array,
        min_value=min_date,
        max_value=max_date,
        help=config_dict.get("help", f"Timezone: {timezone}"),
        format=config_dict.get("format", "YYYY/MM/DD"),
        disabled=config_dict.get("disabled", False),
        label_visibility=config_dict.get("label_visibility", "visible"),
        key=config_dict["widget_uniq_key"],
    )
    if len(displayed_date) == 2:
        AppState.put(start_date_col_name, displayed_date[0])
        AppState.put(end_date_col_name, displayed_date[1])

    return displayed_date


def __render_json(
    body: Union[dict, list, str, Any],
    *,
    expanded: bool = True,
    width: Union[str, int] = "stretch",
):
    """
    Wrapper for st.json with all parameters.
    """
    st.json(body=body, expanded=expanded)


def render_json(df, config_dict):
    """
    Render a JSON object using Streamlit's st.json with configuration parameters.

    Parameters:
    - data (Any): The JSON data to render. expect a df with 1 column having the json.
    The column name should be specified in config_dict with key 'json_column_name'.
    - config_dict (dict): Configuration dictionary containing:
        - json_column_name: Name of the column in the df that contains the JSON object to render.
        - expanded (bool): Whether the JSON should be expanded by default.
        - width (str or int): Width of the JSON display, can be 'stretch' or an integer value.
        - body: If json_column_name is not provided, this will be used as the JSON body to render.
    """
    logging.info("Rendering JSON with configuration: %s", config_dict)
    widget_uniq_key = config_dict.get("widget_uniq_key")
    json_column_name = config_dict.get("json_column_name", None)
    if (
        json_column_name is not None
        and df is not None
        and json_column_name in df.columns
    ):
        body = df[json_column_name].iloc[0]
    else:
        body = config_dict.get("body", None)
    if body is None:
        logging.error(
            f"widget key: {widget_uniq_key}, No JSON data provided. Please provide a valid query which returns df and specify json_column_name in config_dict, or the 'body' key in config_dict."
        )
        raise ValueError(
            "No JSON data provided. Please provide a valid query which returns df with the specified json_column_name, or the 'body' key in config_dict."
        )
    logging.info("Rendering JSON with body: %s", body)
    __render_json(
        body=body,
        expanded=config_dict.get("expanded", True),
        width=config_dict.get("width", "stretch"),
    )


def render_title(df, config_dict: dict):
    """
    Render a title using Streamlit's st.title with configuration parameters.

    Parameters:
    - config_dict (dict): Configuration dictionary containing:
        - body (str): The title text.
        - anchor (str): Optional anchor for the title.
        - help (str): Optional help text.
    - df (Any): this will be ignored, but it is required to match the signature of other render functions.
    """
    logging.info("Rendering title chart with configuration: %s", config_dict)
    st.title(
        body=config_dict.get("body", "Plz set title"),
        anchor=config_dict.get("anchor", False),
        help=config_dict.get("help", "help text for title"),
        width=config_dict.get("width", "content"),
    )


def render_text(df, config_dict: dict):
    """
    Render a title using Streamlit's st.text with configuration parameters.

    Parameters:
    - config_dict (dict): Configuration dictionary containing:
        - body (str): The text.
        - help (str):
    - df (Any): this will be ignored, but it is required to match the signature of other render functions.
    """
    logging.info("Rendering text chart with configuration: %s", config_dict)
    st.text(
        body=config_dict.get("body", "Plz set text"), help=config_dict.get("help", None)
    )


def render_markdown(df, config_dict):
    """
    Render markdown using Streamlit's st.markdown with configuration parameters.

    Parameters:
    - df (Any): this will be ignored, but it is required to match the signature of other render functions.
    - config_dict (dict): Configuration dictionary containing:
        - body (str): The markdown text to render.
        - unsafe_allow_html (bool): Whether to allow HTML in the markdown.
        - help (str): Optional help text.
    """
    logging.info("Rendering markdown with configuration: %s", config_dict)
    st.markdown(
        body=config_dict.get("body", None),
        unsafe_allow_html=config_dict.get("unsafe_allow_html", False),
        help=config_dict.get("help"),
    )


def __render_dataframe(
    data: Union[pd.DataFrame, Any],
    width: Optional[int] = None,
    height: Optional[int] = None,
    *,
    use_container_width: Optional[bool] = None,
    hide_index: Optional[bool] = None,
    column_order: Optional[List[str]] = None,
    key: Optional[str] = None,
    on_select: str = "ignore",  # "ignore" | "rerun"
    selection_mode: str = "multi-row",  # "multi-row" | "single-row"
):
    """
    Wrapper for st.dataframe with all configuration options.
    todo: handle column config
    """
    st.dataframe(
        data=data,
        width=width,
        height=height,
        use_container_width=use_container_width,
        hide_index=hide_index,
        column_order=column_order,
        key=key,
        on_select=on_select,
        selection_mode=selection_mode,
    )


def render_dataframe(data, config_dict):
    """
    Render a DataFrame using Streamlit's st.dataframe with configuration parameters.

    Parameters:
    - data (pd.DataFrame): The DataFrame to render.
    - config_dict (dict): Configuration dictionary containing:
        - width (int): Width of the DataFrame. 0 means default.
        - height (int): Height of the DataFrame. 0 means default.
        - use_container_width (bool): Whether to use the full container width.
        - hide_index (bool): Whether to hide the index column.
        - column_order (list of str): Order of columns to display.
        - on_select (str): Selection behavior ('ignore' or 'rerun').
        - selection_mode (str): Selection mode ('multi-row' or 'single-row').
    """
    logging.info("Rendering dataframe chart with configuration: %s", config_dict)
    # todo: "implement column_config for dataframe."
    __render_dataframe(
        data=data,
        width=config_dict.get("width", 0),
        height=config_dict.get("height", 0),
        use_container_width=config_dict.get("use_container_width", True),
        hide_index=config_dict.get("hide_index", False),
        column_order=config_dict.get("column_order"),
        key=config_dict.get("widget_uniq_key"),
        on_select=config_dict.get("on_select", "ignore"),
        selection_mode=config_dict.get("selection_mode", "multi-row"),
    )


def render_void(void=None, config_dict: dict = None):
    """
    Render an void container.
    DEPRECATED: use render_empty()
    Parameters:
    - data (Any): will be ignored. keeping it,so its in line with other render functions
    - config_dict (dict): Configuration dictionary (optional).
    """
    st.write(" ")  # Empty string to render a void container


def render_empty(void=None, config_dict: dict = None):
    st.empty()


def render_image(df, config_dict: dict):
    st.image(
        image=config_dict.get("image"),
        caption=config_dict.get("caption"),
        width=config_dict.get("width"),
        use_column_width=config_dict.get("use_column_width", True),
        clamp=config_dict.get("clamp", False),
        channels=config_dict.get("channels", "RGB"),
        output_format=config_dict.get("output_format", "auto"),
        use_container_width=config_dict.get("use_container_width", False),
    )


def render_line_chart(data, config_dict):
    """
    Render a line chart using Streamlit's st.line_chart with configuration parameters.

    Parameters:
    - data (pd.DataFrame): The data to plot.
    - config_dict (dict): Configuration dictionary containing:
        - x (str or None): Column name for x-axis (must be in data). If None, index is used.
        - y (str, list of str, or None): Column(s) for y-axis. If None, all columns except x are used.
        - title (str): Optional title to display above the chart.
        - width (int): Width of the chart. 0 means default.
        - height (int): Height of the chart. 0 means default.
        - use_container_width (bool): Whether to use the full container width.
    """
    logging.info("Rendering line chart with configuration: %s", config_dict)
    x = config_dict.get("x")
    y = config_dict.get("y")
    title = config_dict.get("title")
    width = config_dict.get("width", 0)
    height = config_dict.get("height", 0)
    use_container_width = config_dict.get("use_container_width", True)

    __render_line_chart(
        data,
        x=x,
        y=y,
        title=title,
        width=width,
        height=height,
        use_container_width=use_container_width,
        color=config_dict.get("color", None),
    )


def __render_line_chart(
    data,
    x=None,
    y=None,
    title=None,
    width=0,
    height=0,
    use_container_width=True,
    color=["#fd0"],  # noqa: E501
):
    """
    Render a line chart using Streamlit's st.line_chart.

    Parameters:
    - data (pd.DataFrame): The data to plot.
    - x (str or None): Column name to use as x-axis (must be in data). If None, index is used.
    - y (str, list of str, or None): Column(s) to plot on y-axis. If None, all columns except x are used.
    - title (str): Optional title to display above the chart.
    - width (int): Width of the chart. 0 means default.
    - height (int): Height of the chart. 0 means default.
    - use_container_width (bool): Whether to use the full container width.
    """
    if title:
        st.subheader(title)

    if x:
        if y:
            plot_data = data[[x] + ([y] if isinstance(y, str) else y)].set_index(x)
        else:
            plot_data = data.set_index(x)
    else:
        plot_data = data if y is None else data[y]

    st.line_chart(
        plot_data,
        width=width,
        height=height,
        use_container_width=use_container_width,
        color=color,
    )


def __render_selectbox(
    label: str,
    options: Sequence[Any],
    index: int = 0,
    format_func: Callable[[Any], str] = str,
    key: Optional[str] = None,
    help: Optional[str] = None,
    on_change: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
    *,
    placeholder: Optional[str] = None,
    disabled: bool = False,
    label_visibility: str = "visible",  # "visible", "hidden", "collapsed"
) -> Any:
    """
    Full-featured wrapper for st.selectbox.
    """
    return st.selectbox(
        label=label,
        options=options,
        index=index,
        format_func=format_func,
        key=key,
        help=help,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        placeholder=placeholder,
        disabled=disabled,
        label_visibility=label_visibility,
    )


def render_selectbox(data, config_dict: dict):
    """
    Render a select box using Streamlit's st.selectbox with configuration parameters.

    Parameters:
    - data (DataFrame): Data to be used as options in the select box.
    the options will be taken from the specified column in config_dict using the column name specified by key 'options_column_name' in config_dict (defaults to 'options' if not specified). The value for 'options_column_name' be used as placeholder in sql query as '__<options_column_name>__'
    If data is None, options will be taken from config_dict['options']. Optionally, data can also contain an alias column specified by 'alias_column_name' in config_dict (defaults to 'options_column_name' if not specified).
    The alias column is used for display in the UI.
    if u have multiple select box, suggest to have different 'options_column_name' specified for each select box in the config_dict.
    - config_dict (dict): Configuration dictionary containing:
        - label (str): Label for the select box.
        - options (list): List of options to display fallback in case data is None. To pick from data, the config_dict should have the key with name of df column specified as 'options_column_name'.
        - index (int): Default selected index.
        - format_func (callable): Function to format the displayed options.
        - key (str): Unique key for the select box widget.
        - help (str): Optional help text.
        - on_change (callable): Function to call when the selection changes.
        - args (tuple): Arguments to pass to the on_change function.
        - kwargs (dict): Keyword arguments to pass to the on_change function.
        - placeholder (str): Placeholder text when no option is selected.
        - disabled (bool): Whether the select box is disabled.
        - label_visibility (str): Visibility of the label ('visible', 'hidden', 'collapsed').
        - select_box_filter_column (str): must be unique in the app. defaults to <sidebar_heading_name>_<row_idx>_<widget_idx> .This will be used as placeholder in sql query as '__<sidebar_heading_name>_<row_idx>_<widget_idx>__'
    """
    widget_uniq_key = config_dict["widget_uniq_key"]
    logging.info(
        "Rendering selectbox with configuration: %s, widget_uniq_key: %s",
        config_dict,
        widget_uniq_key,
    )

    options_column_name = config_dict.get("options_column_name", "options")
    alias_column_name = config_dict.get("alias_column_name", "options")
    if data is not None and options_column_name in data.columns:
        options = data[options_column_name].tolist()
        aliases = options
        if alias_column_name != options_column_name:
            aliases = data[alias_column_name].tolist()
    else:
        options = config_dict.get("options", [])
        aliases = options

    alias_to_option_map = dict(zip(aliases, options))

    filter_state_key = config_dict.get("options_column_name")
    filter_state_key_alias = filter_state_key + "__alias"
    filter_state_key_idx = filter_state_key + "__idx"

    if AppState.get(filter_state_key_alias) is not None:
        alias_chosen = AppState.get(filter_state_key_alias)
        if alias_chosen is not None:
            default_index = aliases.index(alias_chosen)
        else:
            default_index = config_dict.get("index", 0)
    else:
        default_index = config_dict.get("index", 0)

    alias_chosen = __render_selectbox(
        label=config_dict.get("label", "Select an option"),
        options=aliases,
        index=config_dict.get("index", 0),
        format_func=config_dict.get("format_func", str),
        key=config_dict.get("key", widget_uniq_key),
        help=config_dict.get("help", None),
        on_change=config_dict.get("on_change", None),
        args=config_dict.get("args", None),
        kwargs=config_dict.get("kwargs", None),
        placeholder=config_dict.get("placeholder", ""),
        disabled=config_dict.get("disabled", False),
        label_visibility=config_dict.get("label_visibility", "visible"),
    )
    # save the value selected
    AppState.put(filter_state_key, alias_to_option_map[alias_chosen])
    AppState.put(filter_state_key_alias, alias_chosen)
    AppState.put(filter_state_key_idx, aliases.index(alias_chosen))

    return alias_chosen


def render_metric(df, config_dict):
    """
    Render a metric using Streamlit's st.metric with configuration parameters.
    """
    logging.info("Rendering metric with configuration: %s", config_dict)
    value_column_name = config_dict.get("value_column", "value")
    delta_value_column_name = config_dict.get("delta_value_column", "delta")
    if df is not None and value_column_name in df.columns:
        value = df[value_column_name].iloc[0]
        value if isinstance(value, (str, int, float)) else str(value)
        delta = None
        if delta_value_column_name in df.columns:
            delta = df[delta_value_column_name].iloc[0]
    else:
        raise ValueError(
            f"Column 'Could not get metric from Metric result DataFrame. Check query for widget: {config_dict.get('widget_uniq_key')}."
        )
    st.metric(
        label=config_dict.get("label", ""),
        value=value,
        delta=delta,
        help=config_dict.get("help"),
        label_visibility=config_dict.get("label_visibility", "visible"),
        border=config_dict.get("border", False),
        width=config_dict.get("width", "content"),
    )


def render_bar_chart(data: pd.DataFrame, config_dict: dict):
    """
    Render a bar chart using Streamlit's st.bar_chart with configuration parameters.

    Parameters:
    - data (pd.DataFrame): The data to plot.
    - config_dict (dict): Configuration dictionary containing:
        - x (str or None): Column name for x-axis (must be in data). If None, index is used.
        - y (str, list of str, or None): Column(s) for y-axis. If None, all columns except x are used.
        - x_label (str): Label for the x-axis.
        - y_label (str): Label for the y-axis.
        - color (str, list of str, or None): Color(s) for the bars.
        - horizontal (bool): Whether to render the bars horizontally.
        - stack (bool or str): Stacking configuration ('normalize', 'center', 'layered', None).
        - width (int): Width of the chart. 0 means default.
        - height (int): Height of the chart. 0 means default.
        - use_container_width (bool): Whether to use the full container width.
        - title (str): Optional title to display above the chart.
    """
    logging.info("Rendering bar chart with configuration: %s", config_dict)
    __render_bar_chart(
        data=data,
        x=config_dict.get("x"),
        y=config_dict.get("y"),
        x_label=config_dict.get("x_label"),
        y_label=config_dict.get("y_label"),
        color=config_dict.get("color"),
        horizontal=config_dict.get("horizontal", False),
        stack=config_dict.get("stack", None),
        width=config_dict.get("width", 0),
        height=config_dict.get("height", 0),
        use_container_width=config_dict.get("use_container_width", True),
        title=config_dict.get("title"),
    )


def __render_bar_chart(
    data: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[Union[str, List[str]]] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    color: Optional[Union[str, List[str]]] = None,
    horizontal: bool = False,
    stack: Optional[
        Union[bool, str]
    ] = None,  # Valid: True, False, "normalize", "center", "layered", None
    width: Optional[int] = None,
    height: Optional[int] = None,
    use_container_width: bool = True,
    title: Optional[str] = None,
):
    """
    Render a bar chart using Streamlit's st.bar_chart with all configuration parameters.
    """
    if title:
        st.subheader(title)

    # Don't modify the dataframe — pass x/y as-is to st.bar_chart
    st.bar_chart(
        data=data,
        x=x,
        y=y,
        x_label=x_label,
        y_label=y_label,
        color=color,
        horizontal=horizontal,
        stack=stack,
        width=width,
        height=height,
        use_container_width=use_container_width,
    )


def render_pie_chart(df, config_dict):
    """
    Render a pie chart using Plotly Express and Streamlit.
    :param df:
    :param config_dict:
        - category (str): Column name for categories (default is 'Category').
        - value (str): Column name for values (default is 'Value').
        - title (str): Title of the pie chart.
        - width (int): Width of the chart. 0 means default.
        - height (int): Height of the chart. 0 means default.
    :return:
    """
    import plotly.express as px

    fig = px.pie(
        df,
        names=config_dict.get("category", "Category"),
        values=config_dict.get("value", "Value"),
        title=config_dict.get("title", "Pie Chart"),
        color_discrete_sequence=config_dict.get("color_discrete_sequence", None),
    )
    st.plotly_chart(fig)


def render_map(data, config_dict: dict = {}):
    """
    :param data:    DataFrame containing latitude and longitude columns.
    :param config_dict:
    :return:
    """
    logging.info("Rendering map with configuration: %s", config_dict)
    st.map(
        data=data,
        latitude=config_dict.get("latitude"),
        longitude=config_dict.get("longitude"),
        color=config_dict.get("color"),
        size=config_dict.get("size"),
        zoom=config_dict.get("zoom", 10),
        use_container_width=config_dict.get("use_container_width", True),
        width=config_dict.get("width"),
        height=config_dict.get("height"),
    )


def render_area_chart(
    data: pd.DataFrame,
    config_dict: dict,
):
    """
    Fully parameterized wrapper for st.area_chart.
    """

    st.area_chart(
        data=data,
        x=config_dict.get("x"),
        y=config_dict.get("y"),
        x_label=config_dict.get("x_label"),
        y_label=config_dict.get("y_label"),
        color=config_dict.get("color"),
        stack=config_dict.get("stack", None),
        width=config_dict.get("width", 0),
        height=config_dict.get("height", 0),
        use_container_width=config_dict.get("use_container_width", True),
    )


def render_header(df, config_dict: dict):
    """
    Render a header using Streamlit's st.header with configuration parameters.

    Parameters:
    - config_dict (dict): Configuration dictionary containing:
        - body (str): The header text.
        - anchor (str): Optional anchor for the header.
        - help (str): Optional help text.
        - divider (bool): Whether to show a divider below the header.
    """
    logging.info("Rendering header chart with configuration: %s", config_dict)
    st.header(
        body=config_dict.get("body", "Plz set header"),
        anchor=config_dict.get("anchor", False),
        help=config_dict.get("help"),
        divider=config_dict.get("divider", False),
    )
