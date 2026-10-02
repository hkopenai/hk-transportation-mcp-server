"""Shared fixtures for live integration tests.

These tests hit real upstream APIs (in this server: the Immigration Department
passenger-traffic feed, and potentially others). Running them back-to-back
without any throttle will trip the upstream rate-limiter and produce spurious
failures. The `throttle` fixture below sleeps for a short, configurable
interval before each test so a full ``pytest live_tests`` run stays well
below typical per-second request budgets.

Override the default 1.5-second pause with the ``LIVE_TEST_THROTTLE_S``
environment variable when running against a tighter rate-limit window.
"""

import os
import time
import pytest

DEFAULT_THROTTLE_SECONDS = float(os.environ.get("LIVE_TEST_THROTTLE_S", "1.5"))


@pytest.fixture(autouse=True)
def throttle():
    """Sleep DEFAULT_THROTTLE_SECONDS before every live test."""
    time.sleep(DEFAULT_THROTTLE_SECONDS)
