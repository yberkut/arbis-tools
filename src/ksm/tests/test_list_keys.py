from unittest.mock import patch

from ksm.keys import list_keys


def test_list_keys(tmp_path):
    key_dir = tmp_path / "keys"
    key_dir.mkdir()
    (key_dir / "key1.key").touch()
    (key_dir / "key2.key").touch()

    with patch("ksm.keys.console_message") as mock_console:
        list_keys(key_dir)
        mock_console.assert_any_call("Available keys:")
        mock_console.assert_any_call(" - key1.key")
        mock_console.assert_any_call(" - key2.key")


def test_list_keys_empty(tmp_path):
    key_dir = tmp_path / "empty_keys"
    key_dir.mkdir()

    with patch("ksm.keys.console_message") as mock_console:
        list_keys(key_dir)
        mock_console.assert_called_once_with("No keys found.")


def test_list_keys_no_directory(tmp_path):
    nonexistent_dir = tmp_path / "nonexistent"

    with patch("ksm.keys.error_message") as mock_error:
        list_keys(nonexistent_dir)
        mock_error.assert_called_once_with(f"Directory '{nonexistent_dir}' does not exist.")
