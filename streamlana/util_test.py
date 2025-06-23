import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from streamlana.app_state import AppState
from streamlana.envs import STREAMLANA_TEST_USE_APP_INMEM_STATE
from streamlana.util import get_date, substitute_placeholders

os.environ[STREAMLANA_TEST_USE_APP_INMEM_STATE] = "true"


def test_substitute_placeholders_array():
    query = "select * from table where id in __ids__"
    AppState.put("ids", [1, 2, 3, 4, 5])
    result = substitute_placeholders(query)
    assert result.strip() == "select * from table where id in (1, 2, 3, 4, 5)"


def test_substitute_placeholders():
    query = "SELECT * FROM table"
    result = substitute_placeholders(query)
    assert result == query

    query = """
    SELECT *
    FROM table
    WHERE crash_date >= '__start_date__'
      AND crash_date <= '__end_date__'
      AND status = '__status__'
    """

    AppState.put("start_date", "2024-01-01")
    AppState.put("end_date", "2024-01-31")
    AppState.put("status", "active")
    result = substitute_placeholders(query)
    expected = """
    SELECT *
    FROM table
    WHERE crash_date >= '2024-01-01'
      AND crash_date <= '2024-01-31'
      AND status = 'active'  
    """
    assert result.strip() == expected.strip()


def test_get_date():
    today_dt = datetime.now(ZoneInfo("UTC")).date()
    assert get_date(None) == None
    assert get_date("today") == today_dt

    now = datetime.now(ZoneInfo("UTC"))
    expected_minus_1 = (now - timedelta(days=1)).date()
    assert get_date("today-1") == expected_minus_1
