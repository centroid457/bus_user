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

        victim.add_input("in1")
        assert victim.history == [("in1", [])]
        assert victim.list_input() == ["in1", ]
        assert victim.list_output() == []
        assert victim.as_dict() == {"in1": []}

        victim.add_input("in2")
        assert victim.history == [("in1", []), ("in2", [])]
        assert victim.list_input() == ["in1", "in2"]
        assert victim.list_output() == []
        assert victim.as_dict() == {"in1": [], "in2": []}

        victim.add_output("out2")
        assert victim.history == [("in1", []), ("in2", ["out2", ])]
        assert victim.list_input() == ["in1", "in2"]
        assert victim.list_output() == ["out2", ]

        victim.add_output("out22")
        assert victim.history == [("in1", []), ("in2", ["out2", "out22", ])]
        assert victim.list_input() == ["in1", "in2"]
        assert victim.list_output() == ["out2", "out22", ]

        victim.add_output(["out222", "out2222"])
        assert victim.history == [("in1", []), ("in2", ["out2", "out22", "out222", "out2222", ])]
        assert victim.list_input() == ["in1", "in2"]
        assert victim.list_output() == ["out2", "out22", "out222", "out2222", ]

        victim.print_io()

    def test__add_io__list_last(self):
        victim: HistoryIO = self.VICTIM()
        assert victim.history == []
        assert victim.last_input == ""
        assert victim.last_output == ""

        victim.add_io("in1", "out1")
        assert victim.history == [("in1", ["out1", ]), ]
        assert victim.list_input() == ["in1", ]
        assert victim.list_output() == ["out1", ]
        assert victim.last_input == "in1"
        assert victim.last_output == "out1"

        victim.add_io("in2", ["out2", "out22", ])
        assert victim.history == [("in1", ["out1", ]), ("in2", ["out2", "out22", ]), ]
        assert victim.list_input() == ["in1", "in2"]
        assert victim.list_output() == ["out1", "out2", "out22", ]
        assert victim.last_input == "in2"
        assert victim.last_output == "out22"

    def test__add_history(self):
        victim: HistoryIO = self.VICTIM()
        assert victim.history == []

        history = HistoryIO()
        history.add_io("in1", "out1")

        victim.add_history(history)
        assert victim.history == [("in1", ["out1", ]), ]

    def test__first_output(self):
        victim: HistoryIO = self.VICTIM()
        assert victim.history == []

        victim.add_output("out0")
        assert victim.history == [("", ["out0", ])]
        assert victim.list_input() == ["", ]
        assert victim.list_output() == ["out0"]

        victim.clear()
        assert victim.history == []


# =====================================================================================================================
class Test_BusSerial:
    VICTIM: Type[BusSerial_Base] = type("VICTIM", (BusSerial_Base,), {})
    ports: List[str] = []
    victim_zero: BusSerial_Base = None

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
        self.VICTIM = type("VICTIM", (BusSerial_Base,), {})
        self.victim_zero = self.VICTIM(self.ports[0])

    # -----------------------------------------------------------------------------------------------------------------
    def test__detect_available_ports(self):
        ports = self.VICTIM.detect_available_ports()
        assert len(ports) > 0

    def test__connect_address_existed(self):
        assert BusSerial_Base(address=self.ports[0]).address_check_exists() is True

    def test__connect_address_NOTexisted(self):
        assert BusSerial_Base(address="HELLO").address_check_exists() is False

    def test__usure_bytes(self):
        assert self.VICTIM._data_ensure_bytes("111") == b"111"
        assert self.VICTIM._data_ensure_bytes(b"111") == b"111"

    def test__usure_str(self):
        assert self.VICTIM._data_ensure_string("111") == "111"
        assert self.VICTIM._data_ensure_string(b"111") == "111"

    def test__eol(self):
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

        assert self.victim_zero.write_read_line("hello").last_output == "hello"
        assert self.victim_zero.write_read_line([f"hello{line}" for line in range(3)]).list_output() == [f"hello{line}" for line in range(3)]

        # params -----------------------
        assert self.victim_zero.write_read_line("hello").as_dict() == {"hello": ["hello", ], }

        assert self.victim_zero.write_read_line(["11", "22"]).list_input() == ["11", "22"]
        assert self.victim_zero.write_read_line(["11", "22"]).as_dict() == {"11": ["11", ], "22": ["22", ], }

        history = HistoryIO()
        history.add_io("hello", "hello")
        assert self.victim_zero.write_read_line("hello").as_dict() == history.as_dict()
        assert history.check_equal_io() is True

        history = HistoryIO()
        history.add_io("11", "11")
        history.add_io("22", "22")
        assert self.victim_zero.write_read_line(["11", "22"]).as_dict() == history.as_dict()
        assert history.check_equal_io() is True

    def test__rw_ReadFailPattern(self):
        self.victim_zero.connect()
        try:
            self.victim_zero.write_read_line("123 FAil 123")
        except:
            assert True
        else:
            assert False

        self.victim_zero.RAISE_READ_FAIL_PATTERN = False
        assert self.victim_zero.write_read_line("123 FAil 123").last_output == "123 FAil 123"

    def test__r_all(self):
        self.victim_zero.connect()

        assert self.victim_zero._write_line([f"hello{line}" for line in range(3)]) is True
        assert self.victim_zero._read_line(count=0) == [f"hello{line}" for line in range(3)]


# =====================================================================================================================
class Test_BusSerialWGetattr:
    VICTIM: Type[BusSerialWGetattr_Base] = type("VICTIM", (BusSerialWGetattr_Base,), {})
    ports: List[str] = []
    victim_zero: BusSerialWGetattr_Base = None

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
        self.VICTIM = type("VICTIM", (BusSerialWGetattr_Base,), {})
        self.victim_zero = self.VICTIM(self.ports[0])

    # -----------------------------------------------------------------------------------------------------------------
    # FIX WORK IN FULL PIPELINE!!!!
    def test__getattr(self):
        self.victim_zero.connect()

        assert self.victim_zero.hello().last_output == "hello"
        assert self.victim_zero.hello(123).last_output == "hello 123"
        assert self.victim_zero.hello("?").last_output == "hello ?"

        assert self.victim_zero.hello(f"000{self.victim_zero.EOL.decode()}111{self.victim_zero.EOL.decode()}222").list_output() == ["hello 000", "111", "222"]


# =====================================================================================================================
