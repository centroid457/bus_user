import os
import pytest
import pathlib
import shutil
from tempfile import TemporaryDirectory
from typing import *
from configparser import ConfigParser

from bus_user import *


# =====================================================================================================================
class Test_BusSerial:
    VICTIM: Type[BusSerial] = type("VICTIM", (BusSerial,), {})
    ports: List[str] = []
    victim_zero: BusSerial = None

    @classmethod
    def setup_class(cls):
        cls.ports = cls.VICTIM.detect_available_ports()
        if len(cls.ports) != 1:
            msg = f"[ERROR] need connect only one SerialPort and short Rx+Tx"
            print(msg)
            raise Exception(msg)
        cls.victim_zero = cls.VICTIM(cls.ports[0])

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        self.VICTIM = type("VICTIM", (BusSerial,), {})

    # -----------------------------------------------------------------------------------------------------------------
    def test__detect_available_ports(self):
        ports = self.VICTIM.detect_available_ports()
        assert len(ports) > 0

    def test__connect_address_existed(self):
        assert BusSerial(address=self.ports[0]).check_exists_in_system() is True

    def test__connect_address_NOTexisted(self):
        assert BusSerial(address="HELLO").check_exists_in_system() is False

    def test__usure_bytes(self):
        assert self.VICTIM._data_ensure_bytes("111") == b"111"
        assert self.VICTIM._data_ensure_bytes(b"111") == b"111"

    def test__usure_str(self):
        assert self.VICTIM._data_ensure_string("111") == "111"
        assert self.VICTIM._data_ensure_string(b"111") == "111"

    def test__eol(self):
        # todo: work with several lines???

        self.VICTIM.EOL = b"\n"
        assert self.VICTIM._bytes_eol__ensure(b"111") == b"111\n"
        assert self.VICTIM._bytes_eol__ensure(b"111\n") == b"111\n"
        assert self.VICTIM._bytes_eol__ensure(b"111\n\n") == b"111\n\n"
        assert self.VICTIM._bytes_eol__ensure(b"111\n\n\n") == b"111\n\n\n"     # todo: fix this

        assert self.VICTIM._bytes_eol__clear(b"111") == b"111"
        assert self.VICTIM._bytes_eol__clear(b"111\n") == b"111"
        assert self.VICTIM._bytes_eol__clear(b"111\n\n") == b"111"
        assert self.VICTIM._bytes_eol__clear(b"111\n\n\n") == b"111"

    def test__rw(self):
        self.victim_zero.connect()
        self.victim_zero.write_line("hello")
        assert self.victim_zero.read_line() == "hello"


# =====================================================================================================================
