"""CLI-level tests through main(): exit codes, output, and the import flow."""

import pytest

from aweconfig import cli

ZSHRC = """\
export EDITOR=vi

## Anthropic
export GLM_TOKEN="abc123"

export PLAIN=stay
"""


@pytest.fixture
def vault(tmp_path, monkeypatch):
    path = tmp_path / "keys.env"
    monkeypatch.setenv("AWECONFIG_FILE", str(path))
    return path


def run(capsys, *argv):
    code = cli.main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_init_then_set_list_show_rm(vault, capsys):
    code, out, _ = run(capsys, "init")
    assert code == 0 and "created" in out

    code, _, _ = run(capsys, "set", "MY_KEY", "--value", "sk-secret-value-123")
    assert code == 0

    code, out, _ = run(capsys, "list")
    assert code == 0 and out.splitlines() == ["MY_KEY"]

    code, out, _ = run(capsys, "show", "MY_KEY")
    assert code == 0 and "sk-secret-value-123" not in out and "..." in out

    code, out, _ = run(capsys, "show", "MY_KEY", "--raw")
    assert code == 0 and out.strip() == "sk-secret-value-123"

    code, out, _ = run(capsys, "path")
    assert code == 0 and out.strip() == str(vault)

    code, out, _ = run(capsys, "rm", "MY_KEY")
    assert code == 0
    code, out, err = run(capsys, "show", "MY_KEY")
    assert code == 1 and "not in" in err


def test_set_rejects_bad_name(vault, capsys):
    code, _, err = run(capsys, "set", "BAD-NAME", "--value", "x")
    assert code == 1 and "valid" in err


def test_set_rejects_empty_value(vault, capsys):
    code, _, err = run(capsys, "set", "K", "--value", "")
    assert code == 1 and "empty" in err


def test_no_command_prints_help(capsys):
    code, out, _ = run(capsys)
    assert code == 2 and "usage" in out


def test_import_dry_run_changes_nothing(vault, tmp_path, capsys):
    rc = tmp_path / "zshrc"
    rc.write_text(ZSHRC, encoding="utf-8")
    code, out, _ = run(capsys, "import-zshrc", "--file", str(rc), "--dry-run")
    assert code == 0
    assert "move  GLM_TOKEN" in out and "keep  PLAIN" in out
    assert rc.read_text() == ZSHRC
    assert not vault.exists()


def test_import_with_yes_moves_keys(vault, tmp_path, capsys):
    rc = tmp_path / "zshrc"
    rc.write_text(ZSHRC, encoding="utf-8")
    code, out, _ = run(capsys, "import-zshrc", "--file", str(rc), "--yes")
    assert code == 0
    assert "moved 1 export(s)" in out
    new_rc = rc.read_text()
    assert "GLM_TOKEN" not in new_rc and "export PLAIN=stay" in new_rc
    assert f'source "{vault}"' in new_rc
    assert "## Anthropic" in vault.read_text()
    assert len(list(tmp_path.glob("zshrc.bak-*"))) == 1
