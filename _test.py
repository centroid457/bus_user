import os
import time

import pytest
import pathlib
import shutil
from tempfile import TemporaryDirectory
from typing import *
from configparser import ConfigParser

from bus_user import *


# =====================================================================================================================
class Test_HistoryIO:
    VICTIM: Type[HistoryIO] = type("Victim", (HistoryIO,), {})

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        self.VICTIM = type("Victim", (HistoryIO,), {})

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
    Victim: Type[BusSerial_Base] = type("Victim", (BusSerial_Base,), {})
    victim: BusSerial_Base = None

    @classmethod
    def setup_class(cls):
        if cls.Victim.system_ports__count() != 1:
            msg = f"[ERROR] need connect only one SerialPort and short Rx+Tx"
            print(msg)
            raise Exception(msg)

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        self.Victim = type("Victim", (BusSerial_Base,), {})
        self.Victim.ADDRESS_APPLY_FIRST_VACANT = True
        self.victim = self.Victim()

    def teardown_method(self, method):
        if self.victim:
            self.victim.disconnect()

        self.victim.CMD_PREFIX = ""

    # -----------------------------------------------------------------------------------------------------------------
    def test__ADDRESS_APPLY_FIRST_VACANT(self):
        assert self.victim.connect()
        self.victim.disconnect()

        self.victim.ADDRESS = None

        self.victim.ADDRESS_APPLY_FIRST_VACANT = False
        assert not self.victim.connect(_raise=False)

        self.victim.ADDRESS_APPLY_FIRST_VACANT = True
        assert self.victim.connect(_raise=False)

    def test__connect_multy(self):
        assert self.victim.connect()
        assert self.victim.connect()
        assert self.victim.connect()

    def test__detect_available_ports(self):
        assert self.Victim.system_ports__count() > 0

    # def test__connect_address_existed(self):
    #     assert BusSerial_Base().address_check_exists() is True

    def test__connect_address_NOTexisted(self):
        assert BusSerial_Base(address="HELLO").address_check_exists() is False

    def test__ensure_bytes(self):
        assert self.Victim._data_ensure_bytes("111") == b"111"
        assert self.Victim._data_ensure_bytes(b"111") == b"111"

    def test__ensure_str(self):
        assert self.Victim._data_ensure_string("111") == "111"
        assert self.Victim._data_ensure_string(b"111") == "111"

    def test__eol(self):
        self.Victim.EOL__SEND = b"\n"
        assert self.Victim._bytes_eol__ensure(b"111") == b"111\n"
        assert self.Victim._bytes_eol__ensure(b"111\n") == b"111\n"
        assert self.Victim._bytes_eol__ensure(b"111\n\n") == b"111\n\n"
        assert self.Victim._bytes_eol__ensure(b"111\n\n\n") == b"111\n\n\n"     # todo: fix this

        assert self.Victim._bytes_eol__clear(b"111") == b"111"
        assert self.Victim._bytes_eol__clear(b"111\n") == b"111"
        assert self.Victim._bytes_eol__clear(b"111\n\n") == b"111"
        assert self.Victim._bytes_eol__clear(b"111\n\n\n") == b"111"

    def test__r_w_single(self):
        self.victim.connect()

        # BLANK
        assert self.victim._write_line("") is False
        assert self.victim._read_line() == ""

        assert self.victim._write_line("hello") is True
        assert self.victim._read_line() == "hello"
        assert self.victim._read_line() == ""

        assert self.victim._read_line() == ""

    def test__r_w_multy(self):
        self.victim.connect()

        # RW single ----------------------
        for line in range(3):
            assert self.victim._write_line(f"hello{line}") is True

        for line in range(3):
            assert self.victim._read_line() == f"hello{line}"
        assert self.victim._read_line() == ""

        # W list ----------------------
        assert self.victim._write_line([f"hello{line}" for line in range(3)]) is True
        for line in range(3):
            assert self.victim._read_line() == f"hello{line}"
        assert self.victim._read_line() == ""

        # R list ----------------------
        assert self.victim._write_line([f"hello{line}" for line in range(3)]) is True
        assert self.victim._read_line(3) == [f"hello{line}" for line in range(3)]

        assert self.victim._write_line([f"hello{line}" for line in range(3)]) is True
        assert self.victim._read_line(10) == [f"hello{line}" for line in range(3)]

    def test__rw(self):
        self.victim.connect()

        assert self.victim.write_read_line("hello").last_output == "hello"
        assert self.victim.write_read_line([f"hello{line}" for line in range(3)]).list_output() == [f"hello{line}" for line in range(3)]

        # params -----------------------
        assert self.victim.write_read_line("hello").as_dict() == {"hello": ["hello", ], }

        assert self.victim.write_read_line(["11", "22"]).list_input() == ["11", "22"]
        assert self.victim.write_read_line(["11", "22"]).as_dict() == {"11": ["11", ], "22": ["22", ], }

        history = HistoryIO()
        history.add_io("hello", "hello")
        assert self.victim.write_read_line("hello").as_dict() == history.as_dict()
        assert history.check_equal_io() is True

        history = HistoryIO()
        history.add_io("11", "11")
        history.add_io("22", "22")
        assert self.victim.write_read_line(["11", "22"]).as_dict() == history.as_dict()
        assert history.check_equal_io() is True

    def test__rw_last(self):
        self.victim.connect()

        assert self.victim.write_read_line_last("hello") == "hello"
        assert self.victim.write_read_line_last(["hello1", "hello2"]) == "hello2"

    def test__rw_ReadFailPattern(self):
        self.victim.connect()
        try:
            self.victim.write_read_line("123 FAil 123")
        except:
            assert True
        else:
            assert False

        self.victim.RAISE_READ_FAIL_PATTERN = False
        assert self.victim.write_read_line("123 FAil 123").last_output == "123 FAil 123"

    def test__r_all(self):
        self.victim.connect()

        assert self.victim._write_line([f"hello{line}" for line in range(3)]) is True
        assert self.victim._read_line(count=0) == [f"hello{line}" for line in range(3)]

    def test__pipeline_open_close(self):
        self.victim.connect()

        self.victim.disconnect()
        self.victim = self.Victim()
        self.victim.connect()
        assert self.victim.write_read_line("hello").last_output == "hello"

        self.victim.disconnect()
        self.victim = self.Victim()
        self.victim.connect()
        assert self.victim.write_read_line("hello").last_output == "hello"
        self.victim.disconnect()

    def test__write_args_kwargs(self):
        self.victim.connect()

        assert self.victim.write_read_line("hello").last_output == "hello"
        assert self.victim.write_read_line("hello", args=[1, 2]).last_output == "hello 1 2"
        assert self.victim.write_read_line("hello", kwargs={"CH1": 1}).last_output == "hello CH1=1"
        assert self.victim.write_read_line("hello", args=[1, 2], kwargs={"CH1": 1}).last_output == "hello 1 2 CH1=1"

    def test__CMD_PREFIX(self):
        self.victim.connect()
        self.victim.CMD_PREFIX = "DEV:01:"
        assert self.victim.write_read_line("hello").last_output == f"{self.victim.CMD_PREFIX}hello"
        assert self.victim.write_read_line("hello 12").last_output == f"{self.victim.CMD_PREFIX}hello 12"

        self.victim.CMD_PREFIX = ""
        assert self.victim.write_read_line("hello").last_output == "hello"


# =====================================================================================================================
class Test_BusSerialWGetattr:
    Victim: Type[BusSerial_Base] = type("Victim", (BusSerial_Base,), {})
    victim: BusSerial_Base = None

    @classmethod
    def setup_class(cls):
        if cls.Victim.system_ports__count() != 1:
            msg = f"[ERROR] need connect only one SerialPort and short Rx+Tx"
            print(msg)
            raise Exception(msg)

        cls.Victim = type("Victim", (BusSerial_Base,), {})
        cls.Victim.ADDRESS_APPLY_FIRST_VACANT = True
        cls.victim = cls.Victim()
        cls.victim.connect()

    @classmethod
    def teardown_class(cls):
        if cls.victim:
            cls.victim.disconnect()

    def setup_method(self, method):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    # FIX WORK IN FULL PIPELINE!!!!
    def test__getattr(self):
        assert self.victim.hello() == "hello"
        assert self.victim.hello(12) == "hello 12"
        assert self.victim.hello(12, 13) == "hello 12 13"
        assert self.victim.hello("12 13") == "hello 12 13"
        assert self.victim.hello(CH1=12, CH2=13) == "hello CH1=12 CH2=13"
        assert self.victim.hello(12, CH2=13) == "hello 12 CH2=13"
        assert self.victim.hello("?") == "hello ?"

    def test__GETATTR_SEND_STARTSWITH(self):
        assert self.victim.send__hello() == "hello"

    def test__CMD_PREFIX(self):
        self.victim.CMD_PREFIX = "DEV:01:"
        assert self.victim.hello() == f"{self.victim.CMD_PREFIX}hello"
        assert self.victim.hello(12) == f"{self.victim.CMD_PREFIX}hello 12"
        self.victim.CMD_PREFIX = ""
        assert self.victim.hello() == f"hello"


# =====================================================================================================================
class Test_Emulator:
    Victim: Type[BusSerial_Base] = type("Victim", (BusSerial_Base,), {})
    victim: BusSerial_Base = None

    VictimEmu: Type[DevEmulator_CmdTheme] = type("VictimEmu", (DevEmulator_CmdTheme,), {})
    victim_emu: DevEmulator_CmdTheme = None

    @classmethod
    def setup_class(cls):
        if cls.Victim.system_ports__count() != 2:
            msg = f"[ERROR] need connect TWO SerialPorts and short Rx+Tx between them"
            print(msg)
            raise Exception(msg)

    @classmethod
    def teardown_class(cls):
        if cls.victim:
            cls.victim.disconnect()
        if cls.victim_emu:
            cls.victim_emu.disconnect()

    def setup_method(self, method):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    def test__getattr(self):
        # EMU ---------------
        self.VictimEmu.ADDRESS_APPLY_FIRST_VACANT = True
        self.victim_emu = self.VictimEmu()
        self.victim_emu.start()

        # -------------------
        self.Victim.ADDRESS_APPLY_FIRST_VACANT = True
        self.victim = self.Victim()
        self.victim.connect()

        data = "HELLO 123"
        assert self.victim._write_line(data)

        # time.sleep(2)
        assert self.victim._read_line() == AnswerResult.ERR__NAME_CMD


# =====================================================================================================================
