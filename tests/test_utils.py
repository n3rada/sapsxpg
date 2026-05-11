# tests/test_utils.py

"""Tests for utility functions."""

import pytest
from sapsxpg.utils.methods import check_nwrfc_sdk, nwrfc_sdk_tips


class TestCheckNwrfcSdk:
    def test_returns_bool(self):
        result = check_nwrfc_sdk()
        assert isinstance(result, bool)


class TestNwrfcSdkTips:
    def test_returns_string(self):
        tips = nwrfc_sdk_tips()
        assert isinstance(tips, str)

    def test_contains_env_vars(self):
        tips = nwrfc_sdk_tips()
        assert "SAPNWRFC_HOME" in tips
        assert "LD_LIBRARY_PATH" in tips

    def test_contains_warning(self):
        tips = nwrfc_sdk_tips()
        assert "NWRFCSDK" in tips
