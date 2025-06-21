import logging
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import streamlit

from app_state import AppState


def get_date(value, zone="UTC"):
    if value is None:
        return None
    value = value.lower().strip()

    if value == "today":
        return datetime.now(ZoneInfo(zone)).date()
    elif "today" in value and "-" in value:
        try:
            days_ago = int(value.split("-")[1])
            to_return = (datetime.now(ZoneInfo(zone)) - timedelta(days=days_ago)).date()
            return to_return
        except (IndexError, ValueError):
            raise ValueError(
                "Invalid format. Use 'today' or 'today-N/today+N' where N is an integer."
            )
    elif "today" in value and "+" in value:
        try:
            days_ahead = int(value.split("+")[1])
            to_return = (
                datetime.now(ZoneInfo(zone)) + timedelta(days=days_ahead)
            ).date()
            return to_return
        except (IndexError, ValueError):
            raise ValueError(
                "Invalid format. Use 'today' or 'today-N/today+N' where N is an integer."
            )
    else:
        raise ValueError("Unsupported value. Use 'today' or 'today-N' format.")


def substitute_placeholders(query):
    """
    Finds all placeholders in __ __ and replaces each with values from FilterState.
    :param query:
    :return: final query
    """

    def replacer(match):
        key = match.group(1)
        val = AppState.get(key)
        final_value = val
        if val is None:
            raise KeyError(
                f"Missing key in FilterState: {key}. the widget may not have been rendered yet. Please ensure that the widget is rendered before using its value in a query."
            )
        if isinstance(val, (list, tuple, np.ndarray)):
            final_value = tuple(val)
        return f"{final_value}" if isinstance(final_value, str) else str(final_value)

    final_query = re.sub(r"__([a-zA-Z0-9_]+)__", replacer, query)
    logging.error(f"Final query after substitution: {final_query}")
    return final_query
