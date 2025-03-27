from unittest.mock import patch

from ksm.keys import create_key


def test_create_key(tmp_path):
    key_file = tmp_path / "test.key"
    size = 4096

    with patch("ksm.keys.success_message") as mock_success:
        create_key(key_file, size, dry_run=False)
        assert key_file.exists()
        assert key_file.stat().st_size == size
        mock_success.assert_called_once_with(f"Key '{key_file}' created successfully.")


def test_create_key_dry_run(tmp_path):
    key_file = tmp_path / "test.key"
    size = 4096

    with patch("ksm.keys.dry_run_message") as mock_dry_run:
        create_key(key_file, size, dry_run=True)
        assert not key_file.exists()
        mock_dry_run.assert_called_once_with(f"Would create key: {key_file} ({size} bytes)")


def test_create_key_already_exists(tmp_path):
    key_file = tmp_path / "test.key"
    size = 4096
    key_file.touch()

    with patch("ksm.keys.error_message") as mock_error:
        create_key(key_file, size, dry_run=False)
        mock_error.assert_called_once_with(f"Key '{key_file}' already exists.")
