# tests/test_cli.py

"""Tests for the CLI argument parser."""

import pytest
from sapsxpg.cli import build_parser


class TestBuildParser:
    @pytest.fixture
    def parser(self):
        return build_parser()

    def test_positional_args(self, parser):
        args = parser.parse_args(["host.example.com", "USER", "PASS"])
        assert args.target == "host.example.com"
        assert args.username == "USER"
        assert args.password == "PASS"

    def test_default_client(self, parser):
        args = parser.parse_args(["host", "u", "p"])
        assert args.client == "500"

    def test_custom_client(self, parser):
        args = parser.parse_args(["host", "u", "p", "-c", "100"])
        assert args.client == "100"

    def test_default_sysnr_is_none(self, parser):
        args = parser.parse_args(["host", "u", "p"])
        assert args.sysnr is None

    def test_custom_sysnr(self, parser):
        args = parser.parse_args(["host", "u", "p", "-s", "01"])
        assert args.sysnr == "01"

    def test_load_balanced_connection(self, parser):
        args = parser.parse_args(
            [
                "host",
                "u",
                "p",
                "-m",
                "msgserver",
                "-r",
                "PRD",
                "-g",
                "PUBLIC",
            ]
        )
        assert args.mshost == "msgserver"
        assert args.r3name == "PRD"
        assert args.group == "PUBLIC"

    def test_sysnr_and_mshost_mutually_exclusive(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["host", "u", "p", "-s", "00", "-m", "msgserver"])

    def test_default_timeout(self, parser):
        args = parser.parse_args(["host", "u", "p"])
        assert args.timeout == 30

    def test_custom_timeout(self, parser):
        args = parser.parse_args(["host", "u", "p", "-t", "60"])
        assert args.timeout == 60

    def test_no_trace_flag(self, parser):
        args = parser.parse_args(["host", "u", "p", "--no-trace"])
        assert args.no_trace is True

    def test_trace_default(self, parser):
        args = parser.parse_args(["host", "u", "p"])
        assert args.no_trace is False

    def test_os_choices(self, parser):
        for os_name in ("linux", "windows", "unix", "all", "anyos"):
            args = parser.parse_args(["host", "u", "p", "--os", os_name])
            assert args.os == os_name

    def test_os_invalid(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["host", "u", "p", "--os", "macos"])

    def test_os_default(self, parser):
        args = parser.parse_args(["host", "u", "p"])
        assert args.os is None

    def test_rce_poc_default_command(self, parser):
        args = parser.parse_args(["host", "u", "p", "--rce-poc"])
        assert args.rce_poc == "ZSH"

    def test_rce_poc_custom_command(self, parser):
        args = parser.parse_args(["host", "u", "p", "--rce-poc", "BASH"])
        assert args.rce_poc == "BASH"

    def test_rce_poc_not_set(self, parser):
        args = parser.parse_args(["host", "u", "p"])
        assert args.rce_poc is None

    def test_no_args_fails(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args([])
