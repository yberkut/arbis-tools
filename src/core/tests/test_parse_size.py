import pytest
import click
from core.parse_size import parse_size


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
