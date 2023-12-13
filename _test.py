import os
import pytest
import pathlib
import shutil
from tempfile import TemporaryDirectory
from typing import *
from configparser import ConfigParser

from bus_user import *


# =====================================================================================================================
class Test_HistoryIO:
    VICTIM: Type[HistoryIO] = type("VICTIM", (HistoryIO,), {})

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        self.VICTIM = type("VICTIM", (HistoryIO,), {})

    # -----------------------------------------------------------------------------------------------------------------
    def test__add_list_asdict(self):
        victim: HistoryIO = self.VICTIM()
        assert victim.history == []
        assert victim.as_dict() == {}

        victim.add_input("11")
        assert victim.history == [("11", [])]
        assert victim.list_input() == ["11", ]
        assert victim.list_output() == []
        assert victim.as_dict() == {"11": []}

        victim.add_input("22")
        assert victim.history == [("11", []), ("22", [])]
        assert victim.list_input() == ["11", "22"]
        assert victim.list_output() == []
        assert victim.as_dict() == {"11": [], "22": []}

        victim.add_output("2222")
        assert victim.history == [("11", []), ("22", ["2222", ])]
        assert victim.list_input() == ["11", "22"]
        assert victim.list_output() == ["2222", ]

        victim.add_output("3333")
        assert victim.history == [("11", []), ("22", ["2222", "3333", ])]
        assert victim.list_input() == ["11", "22"]
        assert victim.list_output() == ["2222", "3333", ]

        victim.add_output(["4444", "5555" ])
        assert victim.history == [("11", []), ("22", ["2222", "3333", "4444", "5555", ])]
        assert victim.list_input() == ["11", "22"]
        assert victim.list_output() == ["2222", "3333", "4444", "5555", ]

        victim.print_io()

    def test__add_io(self):
        victim: HistoryIO = self.VICTIM()
        assert victim.history == []

        victim.add_io("11", "1111")
        assert victim.history == [("11", ["1111", ]), ]
        assert victim.list_input() == ["11", ]
        assert victim.list_output() == ["1111", ]

        victim.add_io("22", ["2222", "222222", ])
        assert victim.history == [("11", ["1111", ]), ("22", ["2222", "222222", ]), ]
        assert victim.list_input() == ["11", "22"]
        assert victim.list_output() == ["1111", "2222", "222222", ]

    def test__first_output(self):
        victim: HistoryIO = self.VICTIM()
        assert victim.history == []

        victim.add_output("1111")
        assert victim.history == [("", ["1111"])]
        assert victim.list_input() == ["", ]
        assert victim.list_output() == ["1111"]

        victim.clear()
        assert victim.history == []


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
        # cls.victim_zero = cls.VICTIM(cls.ports[0])

    @classmethod
    def teardown_class(cls):
        if cls.victim_zero:
            cls.victim_zero.disconnect()

    def setup_method(self, method):
        self.VICTIM = type("VICTIM", (BusSerial,), {})
        self.victim_zero = self.VICTIM(self.ports[0])

    # -----------------------------------------------------------------------------------------------------------------
    def test__detect_available_ports(self):
        ports = self.VICTIM.detect_available_ports()
        assert len(ports) > 0

    def test__connect_address_existed(self):
        assert BusSerial(address=self.ports[0]).address_check_exists() is True

    def test__connect_address_NOTexisted(self):
        assert BusSerial(address="HELLO").address_check_exists() is False

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

    def test__r_w_single(self):
        self.victim_zero.connect()

        # BLANK
        assert self.victim_zero._write_line("") is False
        assert self.victim_zero._read_line() == ""

        assert self.victim_zero._write_line("hello") is True
        assert self.victim_zero._read_line() == "hello"
        assert self.victim_zero._read_line() == ""

        assert self.victim_zero._read_line() == ""

    def test__r_w_multy(self):
        self.victim_zero.connect()

        # RW single ----------------------
        for line in range(3):
            assert self.victim_zero._write_line(f"hello{line}") is True

        for line in range(3):
            assert self.victim_zero._read_line() == f"hello{line}"
        assert self.victim_zero._read_line() == ""

        # W list ----------------------
        assert self.victim_zero._write_line([f"hello{line}" for line in range(3)]) is True
        for line in range(3):
            assert self.victim_zero._read_line() == f"hello{line}"
        assert self.victim_zero._read_line() == ""

        # R list ----------------------
        assert self.victim_zero._write_line([f"hello{line}" for line in range(3)]) is True
        assert self.victim_zero._read_line(3) == [f"hello{line}" for line in range(3)]

        assert self.victim_zero._write_line([f"hello{line}" for line in range(3)]) is True
        assert self.victim_zero._read_line(10) == [f"hello{line}" for line in range(3)]

    def test__rw(self):
        self.victim_zero.connect()

        assert self.victim_zero.write_read_line("hello") == "hello"
        assert self.victim_zero.write_read_line([f"hello{line}" for line in range(3)]) == [f"hello{line}" for line in range(3)]

        # params ------------
        assert self.victim_zero.write_read_line("hello") == "hello"













    def test__r_all(self):
        self.victim_zero.connect()

        assert self.victim_zero._write_line([f"hello{line}" for line in range(3)]) is True
        assert self.victim_zero._read_line(count=0) == [f"hello{line}" for line in range(3)]

    def test__getattr(self):
        self.victim_zero.connect()

        assert self.victim_zero.hello() == "hello"
        assert self.victim_zero.hello(123) == "hello 123"
        assert self.victim_zero.hello("?") == "hello ?"

        assert self.victim_zero.hello(f"000{self.victim_zero.EOL.decode()}111{self.victim_zero.EOL.decode()}222") == ["hello 000", "111", "222"]


# =====================================================================================================================
