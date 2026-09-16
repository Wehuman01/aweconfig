"""Tests for the vault store: parse, edit, atomic write, permissions."""

import os

import pytest

from aweconfig import store


@pytest.fixture
def vault(tmp_path, monkeypatch):
    path = tmp_path / "keys.env"
    monkeypatch.setenv("AWECONFIG_FILE", str(path))
    return path


def test_keys_path_override(monkeypatch, tmp_path):
    monkeypatch.setenv("AWECONFIG_FILE", str(tmp_path / "x.env"))
    assert store.keys_path() == tmp_path / "x.env"


def test_init_creates_file_with_0600(vault):
    assert store.init_file(vault) == "created"
    assert vault.exists()
    assert os.stat(vault).st_mode & 0o777 == 0o600
    assert store.HEADER in vault.read_text()


def test_init_is_idempotent_and_reasserts_mode(vault):
    store.init_file(vault)
    os.chmod(vault, 0o644)
    assert store.init_file(vault) == "exists"
    assert os.stat(vault).st_mode & 0o777 == 0o600
    assert vault.read_text().count(store.HEADER) == 1


def test_set_and_read_roundtrip_quoting(vault):
    values = {
        "PLAIN_KEY": "sk-abc123",
        "SPACY": "two words",
        "HAS_QUOTE": "it's here",
        "HAS_DOUBLE": 'say "hi"',
        "HAS_DOLLAR": "$HOME and `cmd`",
    }
    for name, value in values.items():
        store.set_entry(vault, name, value)
    entries = {e.name: e.value for e in store.read_entries(vault)}
    for name, value in values.items():
        assert entries[name] == value


def test_set_replaces_and_preserves_comments(vault):
    vault.write_text("# section A\nexport OLD_KEY='one'\n\n# section B\nexport OTHER='x'\n")
    assert store.set_entry(vault, "OLD_KEY", "two") is True
    text = vault.read_text()
    assert "export OLD_KEY='two'" in text
    assert "# section A" in text and "# section B" in text
    assert "export OTHER='x'" in text
    assert "one" not in text


def test_set_on_missing_file_creates_vault(vault):
    assert store.set_entry(vault, "NEW_KEY", "v") is False
    assert vault.exists()
    assert os.stat(vault).st_mode & 0o777 == 0o600


def test_remove_entry(vault):
    store.set_entry(vault, "GONE_KEY", "v")
    store.set_entry(vault, "STAYS", "v")
    assert store.remove_entry(vault, "GONE_KEY") is True
    assert store.remove_entry(vault, "GONE_KEY") is False
    names = [e.name for e in store.read_entries(vault)]
    assert names == ["STAYS"]


def test_valid_name_rejects_garbage():
    assert store.valid_name("GOOD_NAME_1")
    assert store.valid_name("_PRIVATE")
    assert not store.valid_name("1BAD")
    assert not store.valid_name("BAD-NAME")
    assert not store.valid_name("BAD NAME")


def test_parse_export_variants():
    cases = {
        "export A='sq'": ("A", "sq"),
        'export B="dq"': ("B", "dq"),
        "export C=bare": ("C", "bare"),
        "export D='it'\\''s'": ("D", "it's"),
        'export E="a\\"b"': ("E", 'a"b'),
        "export F='a'\\''b'": ("F", "a'b"),
        "not an export": None,
        "export G=": ("G", ""),
    }
    for line, expected in cases.items():
        entry = store.parse_export(line)
        if expected is None:
            assert entry is None
        else:
            assert (entry.name, entry.value) == expected


def test_mask():
    assert store.mask("abcdefghij123456") == "abcdef...3456"
    assert store.mask("short") == "sh..."
    assert store.mask("ab") == "..."
