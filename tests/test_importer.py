"""Tests for zshrc -> vault migration: planning, rewrite, backup, idempotency."""

import pytest

from aweconfig import importer

ZSHRC = """\
# general settings
export EDITOR=vi
alias ll='ls -la'

## Anthropic
export GLM_TOKEN="abc123"
export KIMI_KEY='k-456'

export LANG=en_US.UTF-8

## Mixed paragraph
export REAL_SECRET='s1'
export KEEP_ME='stay'

## Openai
export OPENAI_KEY="sk-9"
"""


@pytest.fixture
def rc_file(tmp_path):
    path = tmp_path / ".zshrc"
    path.write_text(ZSHRC, encoding="utf-8")
    return path


@pytest.fixture
def vault(tmp_path, monkeypatch):
    path = tmp_path / "keys.env"
    monkeypatch.setenv("AWECONFIG_FILE", str(path))
    return path


def test_plan_selects_whole_secret_paragraphs():
    plan = importer.plan_import(ZSHRC, source_line="SRC")
    assert plan.moved_names == ["GLM_TOKEN", "KIMI_KEY", "OPENAI_KEY"]
    assert "KEEP_ME" in plan.kept
    assert "EDITOR" in plan.kept and "REAL_SECRET" in plan.kept
    # comment headers ride along with moved paragraphs
    moved_text = "\n".join(plan.move_paragraphs[0])
    assert "## Anthropic" in moved_text


def test_plan_extra_names_force_mixed_paragraph():
    plan = importer.plan_import(ZSHRC, extra_names=("KEEP_ME",), source_line="SRC")
    assert "KEEP_ME" in plan.moved_names
    assert "REAL_SECRET" in plan.moved_names  # was already secret


def test_plan_returns_none_when_nothing_matches():
    assert importer.plan_import("export PATH=/bin\n") is None


def test_apply_moves_keys_and_rewrites_rc(rc_file, vault):
    plan = importer.plan_import(ZSHRC, source_line=importer.source_line_for(vault))
    result = importer.apply_import(plan, rc_file, vault)

    new_rc = rc_file.read_text()
    assert "GLM_TOKEN" not in new_rc and "OPENAI_KEY" not in new_rc
    assert "## Anthropic" not in new_rc
    assert 'export EDITOR=vi' in new_rc
    assert 'export KEEP_ME=\'stay\'' in new_rc
    assert importer.source_line_for(vault) in new_rc
    assert result.backup_path.exists()
    assert result.backup_path.read_text() == ZSHRC

    vault_text = vault.read_text()
    assert "## Anthropic" in vault_text and "## Openai" in vault_text
    assert "export GLM_TOKEN='abc123'" in vault_text
    assert "export OPENAI_KEY='sk-9'" in vault_text


def test_apply_skips_names_already_in_vault(rc_file, vault):
    vault.write_text("export GLM_TOKEN='existing'\n")
    plan = importer.plan_import(ZSHRC, source_line=importer.source_line_for(vault))
    result = importer.apply_import(plan, rc_file, vault)
    assert result.skipped_dupes == ["GLM_TOKEN"]
    assert "export GLM_TOKEN='existing'" in vault.read_text()
    assert "export KIMI_KEY='k-456'" in vault.read_text()


def test_second_run_is_idempotent(rc_file, vault):
    plan = importer.plan_import(ZSHRC, source_line=importer.source_line_for(vault))
    importer.apply_import(plan, rc_file, vault)
    rewritten = rc_file.read_text()
    assert importer.plan_import(rewritten, source_line=importer.source_line_for(vault)) is None
    assert rewritten.count(importer.source_line_for(vault)) == 1
