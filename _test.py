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

    def teardown_method(self, method):
        pass

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
class Test_SerialClient:
    Victim: Type[SerialClient] = type("Victim", (SerialClient,), {})
    victim: SerialClient = None

    @classmethod
    def setup_class(cls):
        if cls.Victim.system_ports__count() != 1:
            msg = f"[ERROR] need connect only one SerialPort and short Rx+Tx"
            print(msg)
            raise Exception(msg)

        cls.Victim = type("Victim", (SerialClient,), {})
        cls.Victim.ADDRESS_APPLY_FIRST_VACANT = True
        cls.victim = cls.Victim()
        cls.victim.connect()

    @classmethod
    def teardown_class(cls):
        if cls.victim:
            cls.victim.disconnect()

    def setup_method(self, method):
        self.victim.connect()

    def teardown_method(self, method):
        pass

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

    def test__pipeline_open_close(self):
        self.victim.disconnect()
        self.victim = self.Victim()
        self.victim.connect()
        assert self.victim.write_read_line("hello").last_output == "hello"

        self.victim.disconnect()
        self.victim = self.Victim()
        self.victim.connect()
        assert self.victim.write_read_line("hello").last_output == "hello"
        self.victim.disconnect()

    def test__detect_available_ports(self):
        assert self.Victim.system_ports__count() > 0

    # def test__connect_address_existed(self):
    #     assert SerialClient().address_check_exists() is True

    def test__connect_address_NOTexisted(self):
        assert SerialClient(address="HELLO").address_check_exists() is False

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
        assert self.victim._write_line("") is False
        assert self.victim.read_lines() == []

        assert self.victim._write_line("hello") is True
        assert self.victim.read_lines() == ["hello", ]
        assert self.victim.read_lines() == []

        assert self.victim.read_lines() == []

    def test__r_w_multy(self):
        # RW single ----------------------
        for line in range(3):
            assert self.victim._write_line(f"hello{line}") is True

        for line in range(3):
            assert self.victim.read_line() == f"hello{line}"
        assert self.victim.read_lines() == []

        # W list ----------------------
        assert self.victim._write_line([f"hello{line}" for line in range(3)]) is True
        for line in range(3):
            assert self.victim.read_line() == f"hello{line}"
        assert self.victim.read_lines() == []

        # R list ----------------------
        assert self.victim._write_line([f"hello{line}" for line in range(3)]) is True
        assert self.victim.read_lines() == [f"hello{line}" for line in range(3)]

        assert self.victim._write_line([f"hello{line}" for line in range(3)]) is True
        assert self.victim.read_lines() == [f"hello{line}" for line in range(3)]

    def test__rw(self):
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
        assert self.victim.write_read_line_last("hello") == "hello"
        assert self.victim.write_read_line_last(["hello1", "hello2"]) == "hello2"

    def test__rw_ReadFailPattern(self):
        self.victim.RAISE_READ_FAIL_PATTERN = True
        try:
            self.victim.write_read_line("123 FAil 123")
        except:
            assert True
        else:
            assert False

        self.victim.RAISE_READ_FAIL_PATTERN = False
        assert self.victim.write_read_line("123 FAil 123").last_output == "123 FAil 123"

    def test__r_all(self):
        assert self.victim._write_line([f"hello{line}" for line in range(3)]) is True
        assert self.victim.read_lines() == [f"hello{line}" for line in range(3)]

    def test__write_args_kwargs(self):
        assert self.victim.write_read_line("hello").last_output == "hello"
        assert self.victim.write_read_line("hello", args=[1, 2]).last_output == "hello 1 2"
        assert self.victim.write_read_line("hello", kwargs={"CH1": 1}).last_output == "hello CH1=1"
        assert self.victim.write_read_line("hello", args=[1, 2], kwargs={"CH1": 1}).last_output == "hello 1 2 CH1=1"

    def test__CMD_PREFIX(self):
        self.victim.CMD_PREFIX = "DEV:01:"
        assert self.victim.write_read_line("hello").last_output == f"{self.victim.CMD_PREFIX}hello"
        assert self.victim.write_read_line("hello 12").last_output == f"{self.victim.CMD_PREFIX}hello 12"

        self.victim.CMD_PREFIX = ""
        assert self.victim.write_read_line("hello").last_output == "hello"

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

    def test__getattr__SEND_STARTSWITH(self):
        assert self.victim.send__hello() == "hello"

    def test__getattr_CMD_PREFIX(self):
        self.victim.CMD_PREFIX = "DEV:01:"
        assert self.victim.hello() == f"{self.victim.CMD_PREFIX}hello"
        assert self.victim.hello(12) == f"{self.victim.CMD_PREFIX}hello 12"
        self.victim.CMD_PREFIX = ""
        assert self.victim.hello() == f"hello"


# =====================================================================================================================
class Test_SerialServer_WithConnection:
    Victim: Type[SerialClient] = type("Victim", (SerialClient,), {})
    victim: SerialClient = None

    VictimEmu: Type[SerialServer_Base] = type("VictimEmu", (SerialServer_Base,), {})
    victim_emu: SerialServer_Base = None

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

    def teardown_method(self, method):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    def test__1(self):
        # TODO: use good COM-ports!!! my Profilic is not work correctly!!! but CH341A seems work fine!!!
        # some bytes may be lost or added extra!!!

        # EMU ---------------
        self.VictimEmu.ADDRESS_APPLY_FIRST_VACANT = True
        self.victim_emu = self.VictimEmu()
        self.victim_emu.start()
        # -------------------
        self.Victim.ADDRESS_APPLY_FIRST_VACANT = True
        self.victim = self.Victim()
        self.victim.connect()

        time.sleep(1)
        self.victim._clear_buffer_read()
        assert self.victim.write_read_line("hello").list_output() == self.victim_emu.HELLO_MSG
        # assert self.victim.write_read_line_last("123") == AnswerVariants.ERR__NAME_CMD_OR_PARAM


# =====================================================================================================================
pass    # SerialServer_WithoutDevices
pass    # SerialServer_WithoutDevices
pass    # SerialServer_WithoutDevices
pass    # SerialServer_WithoutDevices
pass    # SerialServer_WithoutDevices


# =====================================================================================================================
class Test_LineParsed:
    Victim: Type[LineParsed] = type("Victim", (LineParsed,), {})
    victim: LineParsed = None

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        self.Victim = type("Victim", (LineParsed,), {})

    def teardown_method(self, method):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    def test__lowercase(self):
        victim = self.Victim("")
        assert victim.LINE == ""
        assert victim.PREFIX == ""
        assert victim.CMD == ""
        assert victim.ARGS == []
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 0

        victim = self.Victim("hello")
        assert victim.LINE == "hello"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == []
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 0

        victim = self.Victim("HELLO")
        assert victim.LINE == "HELLO"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == []
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 0

    def test__args_kwargs(self):
        victim = self.Victim("HELLO CH")
        assert victim.LINE == "HELLO CH"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == ["ch", ]
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 1
        assert victim.KWARGS_count() == 0

        victim = self.Victim("HELLO CH 1")
        assert victim.LINE == "HELLO CH 1"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == ["ch", "1", ]
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 2
        assert victim.KWARGS_count() == 0

        victim = self.Victim("HELLO CH=1")
        assert victim.LINE == "HELLO CH=1"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == []
        assert victim.KWARGS == {"ch": "1"}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 1

        victim = self.Victim("HELLO CH1 CH2=2    ch3=3  ch4")
        assert victim.LINE == "HELLO CH1 CH2=2    ch3=3  ch4"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == ["ch1", "ch4"]
        assert victim.KWARGS == {"ch2": "2", "ch3": "3"}
        assert victim.ARGS_count() == 2
        assert victim.KWARGS_count() == 2

    def test__kwargs_only(self):
        victim = self.Victim("CH=1")
        assert victim.LINE == "CH=1"
        assert victim.PREFIX == ""
        assert victim.CMD == ""
        assert victim.ARGS == []
        assert victim.KWARGS == {"ch": "1"}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 1

    def test__prefix(self):
        victim = self.Victim("HELLO CH 1", _prefix_expected="HELLO")
        assert victim.LINE == "HELLO CH 1"
        assert victim.PREFIX == "hello"
        assert victim.CMD == "ch"
        assert victim.ARGS == ["1", ]
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 1
        assert victim.KWARGS_count() == 0

        victim = self.Victim("HELLO CH 1", _prefix_expected="HELLO123")
        assert victim.LINE == "HELLO CH 1"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == ["ch", "1", ]
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 2
        assert victim.KWARGS_count() == 0

    @pytest.mark.skip
    def test__params_as_noString(self):
        pass    # TODO: add
        pass    # TODO: add
        pass    # TODO: add
        pass    # TODO: add
        pass    # TODO: add
        # victim = self.Victim("HELLO CH")
        # assert victim.LINE == "HELLO CH"
        # assert victim.PREFIX == ""
        # assert victim.CMD == "hello"
        # assert victim.ARGS == ["ch", ]
        # assert victim.KWARGS == {}
        # assert victim.ARGS_count() == 1

    @pytest.mark.skip
    def test__line_as_object(self):
        pass    # TODO: add
        pass    # TODO: add
        pass    # TODO: add
        pass    # TODO: add
        pass    # TODO: add
        # victim = self.Victim("HELLO CH")
        # assert victim.LINE == "HELLO CH"
        # assert victim.PREFIX == ""
        # assert victim.CMD == "hello"
        # assert victim.ARGS == ["ch", ]
        # assert victim.KWARGS == {}
        # assert victim.ARGS_count() == 1


# =====================================================================================================================
class Test_SerialServer_NoConnection:
    Victim: Type[LineParsed] = type("Victim", (LineParsed,), {})
    victim: LineParsed = None

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        self.Victim = type("Victim", (LineParsed,), {})

    def teardown_method(self, method):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    def test__1(self):
        pass
        # victim = self.Victim("")
        # assert victim.LINE == ""
        # assert victim.PREFIX == ""
        # assert victim.CMD == ""
        # assert victim.ARGS == []
        # assert victim.KWARGS == {}


# =====================================================================================================================
