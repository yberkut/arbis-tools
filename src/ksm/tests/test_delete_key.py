from unittest.mock import patch

from ksm.keys import delete_key


def test_delete_key(tmp_path):
    key_file = tmp_path / "test.key"
    key_file.touch()

    with patch("ksm.keys.success_message") as mock_success, \
            patch("ksm.keys.ask_confirm", return_value=True):
        delete_key(key_file, dry_run=False)
        assert not key_file.exists()
        mock_success.assert_called_once_with(f"Key '{key_file}' deleted successfully.")


def test_delete_key_dry_run(tmp_path):
    key_file = tmp_path / "test.key"
    key_file.touch()

    with patch("ksm.keys.dry_run_message") as mock_dry_run, \
            patch("ksm.keys.ask_confirm", return_value=True):
        delete_key(key_file, dry_run=True)
        assert key_file.exists()
        mock_dry_run.assert_called_once_with(f"Would delete key: {key_file}")


def test_delete_key_not_found(tmp_path):
    key_file = tmp_path / "missing.key"

    with patch("ksm.keys.error_message") as mock_error:
        delete_key(key_file, dry_run=False)
        mock_error.assert_called_once_with(f"Key '{key_file}' not found.")


def test_delete_key_aborted(tmp_path):
    key_file = tmp_path / "test.key"
    key_file.touch()

    with patch("ksm.keys.error_message") as mock_error, \
            patch("ksm.keys.ask_confirm", return_value=False):
        delete_key(key_file, dry_run=False)
        assert key_file.exists()
        mock_error.assert_called_once_with("Operation aborted by user.")
