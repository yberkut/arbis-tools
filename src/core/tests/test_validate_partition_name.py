import pytest
import click

from core.validate_partition_name import validate_partition_name


def test_validate_partition_name_valid():
    validate_partition_name("sdb3", "/dev/sdb")


def test_validate_partition_name_invalid_format():
    with pytest.raises(click.exceptions.Abort):
        validate_partition_name("wrong", "/dev/sdb")


def test_validate_partition_name_wrong_device():
    with pytest.raises(click.exceptions.Abort):
        validate_partition_name("sda3", "/dev/sdb")
