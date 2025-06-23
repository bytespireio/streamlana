import base64
import hashlib
import json
import logging
import os
import traceback
from typing import Callable, Literal
from importlib.resources import files

import duckdb
import streamlit as st
from streamlit.commands.page_config import InitialSideBarState, Layout

from streamlana import chart_helpers
from streamlana.envs import (
    STREAMLANA_DEBUG_DF,
    STREAMLANA_DEBUG_STATE,
    STREAMLANA_URL_PG_NAME_PREFIX,
)
from streamlana.util import substitute_placeholders


def debug_df(df):
    # todo implement
    print(df.head(5).astype(str).to_string(index=False))


def get_page_name_for_url(full_name: str, pg_anonymous=False) -> str:
    """Generate a URL-friendly name for the page.
    If the environment variable STREAMLANA_ANONYMOUS_PG_NAMES is set to "true",
    it will return a short hash of the full name.
    Otherwise, it will replace spaces and dashes with underscores and convert to lowercase.
    :param full_name: The full name of the page.
    :param pg_anonymous: If True, use a short hash for the page name.
    :return: A URL-friendly name for the page.
    """

    if pg_anonymous:
        logging.info("Using short name for page: %s", full_name)
        return short_hash(full_name)

    return full_name.replace(" ", "_").replace("-", "_").lower()


def short_hash(s, length=8):
    return hashlib.sha256(s.encode()).hexdigest()[:length]


def set_markdown_with_icon(icon_path: str = None, markdown_style: str = ""):
    """
    Set the favicon for the Streamlit application.

    :param icon_path: Path to the icon file.
    """
    if icon_path is None:
        icon_path = files("streamlana").joinpath("streamlana.ico")
    with open(icon_path, "rb") as icon_file:
        encoded = base64.b64encode(icon_file.read()).decode()
    favicon_data_url = f"data:image/x-icon;base64,{encoded}"
    st.markdown(
        markdown_style
        + f"""
        <link rel="icon" href="{favicon_data_url}">
        <script>
          var link = document.querySelector("link[rel~='icon']");
          if (!link) {{
            link = document.createElement('link');
            link.rel = 'icon';
            document.getElementsByTagName('head')[0].appendChild(link);
          }}
          link.href = "{favicon_data_url}";
        </script>
        """,
        unsafe_allow_html=True,
    )


def auth_enabled(auth_session_state_key_name) -> bool:
    """
    Check if authentication is enabled based on session state key.

    :param auth_session_state_key_name: Key name in session state to check for authentication.
    :return: True if authentication is enabled, False otherwise.
    """
    return auth_session_state_key_name is not None


def load_side_bar_config_yaml(side_bar_config_file_path):
    """
    Load sidebar configuration from a YAML file.

    :param side_bar_config_file_path: Path to the YAML file containing sidebar configuration.
    :return: Parsed sidebar configuration as a list of dictionaries.
    """
    import yaml

    try:
        with open(side_bar_config_file_path, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logging.error(
            "Failed to load sidebar configuration from file: %s",
            side_bar_config_file_path,
        )
        traceback.print_exc()
        raise e
    return config.get("side_bar", [])


def __create_dynamic_func(
    full_name: str, config_dict, duckbdb_conn, pg_anonymous=False
):
    name_in_url = get_page_name_for_url(full_name, pg_anonymous=pg_anonymous)

    prefix = os.environ.get(STREAMLANA_URL_PG_NAME_PREFIX, "pg_")
    func_name = f"{prefix}{name_in_url}"

    def _template():
        render_dashboard(full_name, config_dict, duckbdb_conn=duckbdb_conn)

    _template.__name__ = func_name  # Change the function’s __name__ attribute
    globals()[func_name] = _template  # Inject into global namespace

    return globals()[func_name]


def default_check_user_access() -> str:
    """Check if the user has access to pages.
    :param Any: Placeholder for any input
    :return: None if not authorized, Username if allowed (return "guest" if auth disabled)
    """
    # Assuming that auth is disabled.
    return "guest"


def render_side_bar_pages(
    side_bar_config: dict,
    duckbdb_conn,
    markdown_style: str = "",
    logo_path: str = None,
    logo_size: Literal["small", "medium", "large"] = "large",
    icon=None,
    check_user_access: Callable[[], str] = default_check_user_access,
):
    """Render sidebar pages based on the provided configuration.
    :param side_bar_config: Configuration for sidebar pages.
    :param duckbdb_conn: DuckDB connection object.
    :param markdown_style: Custom CSS for sidebar links.
    :param logo_path: Path to the logo image.
    :param logo_size: Size of the logo. small, medium, large.
    :param icon: Path to the icon file for the favicon.
    :param check_user_access: Function to check user access and return username.
    """
    # set_page_layout(
    #     initial_sidebar_state="expanded",
    #     layout="wide",
    #     page_icon="streamlana.ico",
    # )
    username = "guest"
    if check_user_access is not None:
        username = check_user_access()
        if username is None:
            logging.warning(
                "check_user_access returned 'None' username. User is not allowed to access pages. Returning without rendering sidebar pages."
            )
            return
    else:
        logging.warning(
            "check_user_access callback is None. will assume auth is disabled. username set to guest."
        )

    logging.info("username obtained from check_user_access callabck: %s", username)
    # Track selected file in session state
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = None

    set_markdown_with_icon(icon_path=icon, markdown_style=markdown_style)

    if logo_path == "" or logo_path is None:
        logo_path = files("streamlana").joinpath("streamlana.png")

    st.logo(logo_path, size=logo_size)

    # Create a dictionary to hold pages
    pages = {}
    for section in side_bar_config:
        ordered_pages = []
        heading = section.get("heading", "")
        if heading == "":
            raise ValueError(
                "heading is required for each section in side_bar_config. "
                "Please provide a valid heading."
            )
        page_sections = section.get("pages", None)
        if pages is None:
            raise ValueError(
                f"pages are required for section: '{heading}'. "
                "Please provide a valid list of pages."
            )
        for pg_section in page_sections:
            name = pg_section.get("name", "")
            pg_enabled = pg_section.get("enabled", True)
            pg_anonymous = pg_section.get("anonymous", False)
            if not pg_enabled:
                logging.info(
                    f"Page '{name}' in section '{heading}' is disabled, skipping rendering."
                )
                continue
            if name.strip() == "":
                raise ValueError(
                    f"name is required for each page in section: '{heading}'. "
                    "Please provide a valid name."
                )

            path_to_py = pg_section.get("code_definition", None)
            if path_to_py is not None:
                url_path = get_page_name_for_url(name, pg_anonymous=pg_anonymous)
                ordered_pages.append(st.Page(path_to_py, title=name, url_path=url_path))
            else:
                config_file_path = pg_section.get("config_file_path")
                if config_file_path is None:
                    raise ValueError(
                        f"since path to custom python module not specified for page, page config file path is required for page: '{name}'"
                    )
                try:
                    with open(config_file_path, "r") as f:
                        config_dict = json.load(f)
                        callable_render = __create_dynamic_func(
                            name, config_dict, duckbdb_conn, pg_anonymous=pg_anonymous
                        )
                        ordered_pages.append(st.Page(callable_render, title=name))
                except Exception as e:
                    logging.error("error reading the config file: %s", config_file_path)
                    traceback.print_exc()
                    st.error("⚠ Error reading config file: %s" % config_file_path)
                    raise e

        pages[heading] = ordered_pages
    pg = st.navigation(pages, position="sidebar", expanded=True)
    pg.run()
    if os.environ.get(STREAMLANA_DEBUG_STATE, "false").lower() == "true":
        st.sidebar.subheader("Session State Debug")
        st.sidebar.json(st.session_state.to_dict())


def set_page_layout(
    page_title="StreamLana",
    page_icon=None,
    layout: Layout = "wide",
    initial_sidebar_state: InitialSideBarState = "expanded",
):
    """
    Set the  Length of Width distribution arraypage layout for Streamlit application.
    call it only once. at the top of your application.
    """
    if page_icon is None:
        page_icon = files("streamlana").joinpath("streamlana.ico")

    if "_layout" not in st.session_state:
        st.session_state._layout = layout
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=st.session_state._layout,  # Optional: "centered" or "wide"
        initial_sidebar_state=initial_sidebar_state,  # Optional: "expanded" or "collapsed",
        menu_items={
            "Get help": "https://github.com/jaihind213/streamlana",
            "About": "Streamlit in Grafana style. Business Intelligence as Configuration",
        },
    )


def render_dashboard(dashboard_name: str, page_config_dict, duckbdb_conn=None):
    title = page_config_dict.get("page_title", "")
    if title is not None and title.strip() != "":
        st.title(title)

    page_rows = page_config_dict.get("page_rows", [])
    num_rows_in_page = len(page_rows)
    logging.info(
        "Rendering dashboard: %s with %d rows", dashboard_name, num_rows_in_page
    )
    for row_idx, row in enumerate(page_rows):
        widgets_width_distribution = row.get("widgets_width_spec", [])
        with_expander = row.get(
            "with_expander", {"label": f"Row {row_idx} Widgets...", "expanded": False}
        )
        widgets_gap = row.get("widgets_gap", "small")
        widgets_v_alignment = row.get("widgets_vertical_alignment", "top")
        widgets_have_border = row.get("widgets_border", False)
        widgets = row.get("widgets", [])
        if len(widgets) != len(widgets_width_distribution):
            raise ValueError(
                f"Length of 'widgets_width_spec' array: {len(widgets_width_distribution)}, does not match number of widgets: len(widgets) in row:{row_idx} of page '{dashboard_name}'."
            )
        logging.info(
            "Rendering row in dashboard: %s ,with width distribution: %s",
            dashboard_name,
            widgets_width_distribution,
        )
        if with_expander is not None:
            with st.expander(
                label=with_expander.get("label", ""),
                expanded=with_expander.get("expanded", False),
            ):
                cols = st.columns(
                    widgets_width_distribution,
                    gap=widgets_gap,
                    vertical_alignment=widgets_v_alignment,
                    border=widgets_have_border,
                )
        else:
            cols = st.columns(
                widgets_width_distribution,
                gap=widgets_gap,
                vertical_alignment=widgets_v_alignment,
                border=widgets_have_border,
            )

        logging.info(
            "Rendering dashboard: %s with %d widgets", dashboard_name, len(widgets)
        )
        for widget_idx, widget in enumerate(widgets):
            widget_enabled = widget.get("widget_enabled", True)
            if not widget_enabled:
                logging.info(
                    f"Widget at index {widget_idx} in row {row_idx} is disabled, skipping rendering."
                )
                chart_helpers.render_void()
                continue
            query = widget.get("query", "select 1 as dummy_result")
            config = widget.get("config", {})
            config["widget_uniq_key"] = f"{dashboard_name}_{row_idx}_{widget_idx}"
            widget_type = widget.get("type", None)
            if widget_type is None or "" == widget_type.strip():
                raise ValueError(
                    f"Widget type is required for widget at index {widget_idx} in row {row_idx}, dashboard: {dashboard_name}"
                )

            # Run the query to get a dataframe
            final_query = substitute_placeholders(query)
            logging.info(
                f"Executing final query: {final_query} for widget type: {widget_type} with config: {config}, page_row: {row_idx}, widget_idx: {widget_idx}, dashboard: {dashboard_name}"
            )
            # Execute the query
            if duckbdb_conn is None:
                logging.warning(
                    "DuckDB connection is not provided, creating a new connection."
                )
                duckbdb_conn = duckdb.connect()
            try:
                df = duckbdb_conn.execute(final_query).df()
                if os.environ.get(STREAMLANA_DEBUG_DF, "false") == "true":
                    debug_df(df)
            except Exception as e:
                logging.error(
                    f"Error executing query: {final_query} for widget type: {widget_type}, dashboard: {dashboard_name}, row: {row_idx}, widget_idx: {widget_idx}"
                )
                traceback.print_exc()
                with cols[widget_idx]:
                    chart_helpers.render_rendering_failure(
                        "⚠ Query Failed.\n\n check logs", None
                    )
                continue

            # Dispatch to the appropriate render function
            render_fn = getattr(chart_helpers, f"render_{widget_type}", None)

            if callable(render_fn):
                try:
                    with cols[widget_idx]:
                        render_fn(df, config)
                except Exception as e:
                    logging.error(
                        f"Error rendering widget type: {widget_type}, dashboard: {dashboard_name}, row: {row_idx}, widget_idx: {widget_idx}"
                    )
                    traceback.print_exc()
                    with cols[widget_idx]:
                        chart_helpers.render_rendering_failure(
                            "⚠ Render Error.\n\n Check Logs", None
                        )
                    continue
            else:
                with cols[widget_idx]:
                    st.error(
                        f"Unsupported widget type: {widget_type}, dashboard: {dashboard_name}, row: {row_idx}, widget_idx: {widget_idx}"
                    )
