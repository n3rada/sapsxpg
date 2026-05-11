# tests/test_sap.py

"""Tests for SAP system logic that does not require a live connection."""

import pytest
from sapsxpg.core.sap import get_os_variants


class TestGetOsVariants:
    def test_linux_includes_unix(self):
        variants = get_os_variants("linux")
        assert "linux" in variants
        assert "unix" in variants
        assert "anyos" in variants

    def test_windows_variants(self):
        variants = get_os_variants("windows")
        assert "windows" in variants
        assert "windows nt" in variants
        assert "anyos" in variants

    def test_unix_includes_linux(self):
        variants = get_os_variants("unix")
        assert "unix" in variants
        assert "linux" in variants
        assert "anyos" in variants

    def test_all_returns_many(self):
        variants = get_os_variants("all")
        assert "linux" in variants
        assert "windows" in variants
        assert "unix" in variants
        assert "anyos" in variants
        assert len(variants) > 5

    def test_anyos_returns_only_anyos(self):
        variants = get_os_variants("anyos")
        assert variants == ["anyos"]

    def test_sunos_includes_unix(self):
        variants = get_os_variants("sunos")
        assert "sunos" in variants
        assert "unix" in variants
        assert "anyos" in variants

    def test_aix_includes_unix(self):
        variants = get_os_variants("aix")
        assert "aix" in variants
        assert "unix" in variants
        assert "anyos" in variants

    def test_unknown_os_fallback(self):
        variants = get_os_variants("freebsd")
        assert "anyos" in variants
        assert "freebsd" in variants

    def test_case_insensitive(self):
        variants = get_os_variants("Linux")
        assert "linux" in variants
        assert "unix" in variants
