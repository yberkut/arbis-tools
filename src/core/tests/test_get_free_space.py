from unittest.mock import patch

from core.get_free_space import get_free_space


@patch("subprocess.run")
def test_get_free_space(mock_run):
    mock_run.return_value.stdout = '''
Number  Start   End     Size    File system  Name  Flags
        1049kB  2097kB  1049kB  Free Space
 1      2097kB  3146kB  1049kB  ext4
        3146kB  1049MB  1046MB  Free Space
'''
    result = get_free_space("/dev/sdb")
    assert result == [("1049kB", "2097kB"), ("3146kB", "1049MB")]
