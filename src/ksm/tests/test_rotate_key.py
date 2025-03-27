from unittest.mock import patch

from ksm.keys import rotate_key


def test_rotate_key_dry_run(tmp_path):
    key_file = tmp_path / "test.key"
    key_file.touch()

    with patch("ksm.keys.dry_run_message") as mock_dry_run:
        rotate_key("test.key", "/dev/mapper/test-luks", 1, dry_run=True)
        mock_dry_run.assert_any_call("Would check existing LUKS slots in /dev/mapper/test-luks")
        mock_dry_run.assert_any_call("Would add new key from test.key to slot 1 in /dev/mapper/test-luks")
        mock_dry_run.assert_any_call("Would remove key from slot 1 in /dev/mapper/test-luks")


def test_rotate_key_key_not_found():
    with patch("ksm.keys.error_message") as mock_error:
        rotate_key("nonexistent.key", "/dev/mapper/test-luks", 1, dry_run=False)
        mock_error.assert_called_once_with("Key 'nonexistent.key' not found.")
