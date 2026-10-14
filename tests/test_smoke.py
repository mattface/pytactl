# Copyright (c) 2026 Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause

"""Minimal smoke tests that confirm the pytest setup itself is functional.

These intentionally stay on the import/CLI-parser path and avoid the hardware
and config-loading code, so they run with no debug board attached. Deeper board
and config coverage lives in the dedicated test suite.
"""

import os

import pytest

import pytactl
from pytactl import cli
from pytactl.cli import build_parser, main


def test_version_is_defined():
    assert isinstance(pytactl.__version__, str) and pytactl.__version__


def test_default_tac_config_path_points_into_package():
    path = pytactl.PACKAGE_TAC_CONFIG_PATH
    assert os.path.basename(path) == "tac_configs"
    assert path.startswith(os.path.dirname(pytactl.__file__))
    assert os.path.isdir(path)


def test_parser_dispatches_subcommand():
    parser = build_parser()
    args = parser.parse_args(["list"])
    assert args.mode == "list"


def test_listconfigs_exits_nonzero_without_a_device_list(tmp_path, capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["listconfigs", "--tac-config-path", str(tmp_path)])
    assert excinfo.value.code == 1
    assert "Cannot read devicelist.json" in capsys.readouterr().out


def test_listconfigs_lists_the_bundled_configs(capsys):
    main(["listconfigs", "--tac-config-path", pytactl.PACKAGE_TAC_CONFIG_PATH])
    out = capsys.readouterr().out
    assert "bundled with pytactl" in out
    assert pytactl.BUNDLED_DEFAULT_CONFIG_FILENAME in out


def test_falling_back_to_installed_configs_warns(tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(cli, "INSTALLED_TAC_CONFIG_PATH", str(tmp_path))
    monkeypatch.setattr(cli, "default_tac_config_path", lambda: str(tmp_path))

    with pytest.raises(SystemExit):
        main(["listconfigs"])

    assert "deprecated 'installconfigs'" in caplog.text


def test_explicit_config_path_does_not_warn(tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(cli, "INSTALLED_TAC_CONFIG_PATH", str(tmp_path))
    monkeypatch.setattr(cli, "default_tac_config_path", lambda: str(tmp_path))

    with pytest.raises(SystemExit):
        main(["listconfigs", "--tac-config-path", str(tmp_path)])

    assert "deprecated 'installconfigs'" not in caplog.text
