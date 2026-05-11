# tests/test_banner.py

"""Tests for banner display."""

from sapsxpg.banner import display_banner
from sapsxpg import __version__


class TestBanner:
    def test_returns_string(self):
        result = display_banner()
        assert isinstance(result, str)

    def test_contains_version(self):
        result = display_banner()
        assert __version__ in result

    def test_contains_name(self):
        result = display_banner()
        assert "SXPG_CALL_SYSTEM" in result
