import pytest
import click
from core.utils import parse_size, validate_partition_name, get_free_space
from unittest.mock import patch


@pytest.mark.parametrize("input_str, expected", [
    ("2G", 2_097_152),
    ("2GiB", 2_097_152),
    ("120M", 122_880),
    ("120MiB", 122_880),
    ("1GB", 1_048_576),
    ("500MB", 512_000),
    ("1049kB", 1_049),
    ("1044k", 1_044),
    ("500KiB", 500),
])
def test_parse_size(input_str, expected):
    assert parse_size(input_str) == expected


def test_parse_size_invalid():
    with pytest.raises(click.exceptions.Abort):
        parse_size("invalid")


def test_validate_partition_name_valid():
    validate_partition_name("sdb3", "/dev/sdb")  # Не повинно викликати помилку


def test_validate_partition_name_invalid_format():
    with pytest.raises(click.exceptions.Abort):
        validate_partition_name("wrong", "/dev/sdb")


def test_validate_partition_name_wrong_device():
    with pytest.raises(click.exceptions.Abort):
        validate_partition_name("sda3", "/dev/sdb")


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
