import pytest
from typing import *

import time
import pathlib
import shutil
from tempfile import TemporaryDirectory

from bus_user import *
from pytest_aux import *


# =====================================================================================================================
@pytest.mark.parametrize(argnames="func_link", argvalues=[SerialClient._data_ensure__bytes, ])
@pytest.mark.parametrize(
    argnames="args, _EXPECTED",
    argvalues=[
        (111, Exception),
        (str, Exception),

        ("", b""),
        ("\r", b"\r"),
        ("\r\n", b"\r\n"),
        ("\n", b"\n"),
        ("str", b"str"),
        ("str\n", b"str\n"),
        ("str\r\n", b"str\r\n"),

        (b"", b""),
        (b"\r", b"\r"),
        (b"\r\n", b"\r\n"),
        (b"\n", b"\n"),
        (b"str", b"str"),
        (b"str\n", b"str\n"),
        (b"str\r\n", b"str\r\n"),
    ]
)
def test__data_ensure__bytes(func_link, args, _EXPECTED):
    pytest_func_tester__wo_kwargs(func_link, args, _EXPECTED)


# =====================================================================================================================
