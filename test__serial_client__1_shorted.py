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
class Test__AddressResolved:
    Victim: Type[SerialClient]
    victim: SerialClient

    @classmethod
    def setup_class(cls):
        class Victim(SerialClient):
            ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED
            RAISE_CONNECT = False

            def address__answer_validation(self):
                return self.address__answer_validation__shorted()

        cls.Victim = Victim

    # @classmethod
    # def teardown_class(cls):
    #     pass
    #
    # def setup_method(self, method):
    #     pass
    #
    # def teardown_method(self, method):
    #     pass
    #     if self.victim:
    #         self.victim.disconnect()

    # -----------------------------------------------------------------------------------------------------------------
    def test__1(self):
        victim = self.Victim()
        assert victim.address_check__resolved() is False
        assert victim.connect() is True
        assert victim.address_check__resolved() is True
        victim.disconnect()
        assert victim.address_check__resolved() is True

        victim.ADDRESS = None
        assert victim.address_check__resolved() is False

        victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED
        assert victim.address_check__resolved() is False
        assert victim.connect() is True
        assert victim.address_check__resolved() is True


# =====================================================================================================================
class Test__Shorted:
    Victim: Type[SerialClient]
    victim: SerialClient

    @classmethod
    def setup_class(cls):
        class Victim(SerialClient):
            ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED

            def address__answer_validation(self):
                return self.address__answer_validation__shorted()

        cls.Victim = Victim
        cls.victim = cls.Victim()
        if not cls.victim.connect():
            msg = f"[ERROR] not found PORT shorted by Rx+Tx"
            print(msg)
            raise Exception(msg)

    @classmethod
    def teardown_class(cls):
        if cls.victim:
            cls.victim.disconnect()

    def setup_method(self, method):
        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED
        self.victim.connect(_raise=False)

    def teardown_method(self, method):
        pass
        if self.victim:
            self.victim.disconnect()

    # -----------------------------------------------------------------------------------------------------------------
    def test__ADDRESS__FIRST_VACANT(self):
        self.victim.disconnect()

        self.victim.ADDRESS = None
        assert not self.victim.connect(_raise=False)

        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE
        assert self.victim.connect(_raise=False)

        assert isinstance(self.victim.ADDRESS, str)

    def test__ADDRESS__FIRST_SHORTED(self):
        self.victim.disconnect()

        self.victim.ADDRESS = None
        assert not self.victim.connect(_raise=False)

        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED
        assert self.victim.connect(_raise=False)
        assert self.victim.addresses_shorted__count() > 0

    def test__ADDRESS__FIRST_ANSWER_VALID(self):
        self.victim.disconnect()

        self.victim.ADDRESS = None
        assert not self.victim.connect(_raise=False)

        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__ANSWER_VALID
        assert self.victim.connect(_raise=False)

        # ==============
        self.victim.disconnect()
        class Victim(SerialClient):
            ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__ANSWER_VALID
            def address__answer_validation(self) -> Union[bool, NoReturn]:
                raise Exception()

        assert not Victim().connect(_raise=False)

    def test__connect_multy(self):
        assert self.victim.connect(_raise=False)
        assert self.victim.connect(_raise=False)
        assert self.victim.connect(_raise=False)

    def test__recreate_object(self):
        self.victim.disconnect()
        self.victim = self.Victim()
        assert self.victim.connect(_raise=False)
        assert self.victim.write_read("hello").last_output == "hello"

        self.victim.disconnect()
        self.victim = self.Victim()
        self.victim.connect(_raise=False)
        assert self.victim.write_read("hello").last_output == "hello"
        self.victim.disconnect()

    def test__detect_available_ports(self):
        assert self.Victim.addresses_system__count() > 0

    def test__connect_address_NOTexisted(self):
        assert SerialClient(address="HELLO").address__check_exists() is False

    def test__ensure_bytes(self):
        assert self.Victim._data_ensure__bytes("111") == b"111"
        assert self.Victim._data_ensure__bytes(b"111") == b"111"

    def test__ensure_str(self):
        assert self.Victim._data_ensure__string("111") == "111"
        assert self.Victim._data_ensure__string(b"111") == "111"

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

    def test__wr_single(self):
        assert self.victim._write("") is True
        assert self.victim.read_lines() == []

        assert self.victim._write("hello") is True
        assert self.victim.read_lines() == ["hello", ]
        assert self.victim.read_lines() == []

    def test__wr_multy(self):
        # RW single ----------------------
        for line in range(3):
            assert self.victim._write(f"hello{line}") is True

        for line in range(3):
            assert self.victim.read_line() == f"hello{line}"
        assert self.victim.read_lines() == []

        # W list ----------------------
        assert self.victim._write([f"hello{line}" for line in range(3)]) is True
        for line in range(3):
            assert self.victim.read_line() == f"hello{line}"
        assert self.victim.read_lines() == []

        # R list ----------------------
        assert self.victim._write([f"hello{line}" for line in range(3)]) is True
        assert self.victim.read_lines() == [f"hello{line}" for line in range(3)]

        assert self.victim._write([f"hello{line}" for line in range(3)]) is True
        assert self.victim.read_lines() == [f"hello{line}" for line in range(3)]

    def test__wr(self):
        assert self.victim.write_read("hello").last_output == "hello"
        assert self.victim.write_read([f"hello{line}" for line in range(3)]).list_output() == [f"hello{line}" for line in range(3)]

        # params -----------------------
        assert self.victim.write_read("hello").as_dict() == {"hello": ["hello", ], }

        assert self.victim.write_read(["11", "22"]).list_input() == ["11", "22"]
        assert self.victim.write_read(["11", "22"]).as_dict() == {"11": ["11", ], "22": ["22", ], }

        history = HistoryIO()
        history.add_io("hello", "hello")
        assert self.victim.write_read("hello").as_dict() == history.as_dict()
        assert history.check_equal_io() is True

        history = HistoryIO()
        history.add_io("11", "11")
        history.add_io("22", "22")
        assert self.victim.write_read(["11", "22"]).as_dict() == history.as_dict()
        assert history.check_equal_io() is True

    def test__wr_last(self):
        assert self.victim.write_read__last("hello") == "hello"
        assert self.victim.write_read__last(["hello1", "hello2"]) == "hello2"

    def test__wr_last_validate(self):
        assert self.victim.write_read__last_validate("hello", "hello")
        assert self.victim.write_read__last_validate(["hello1", "hello2"],  "hello2")

    def test__wr_ReadFailPattern(self):
        self.victim.RAISE_READ_FAIL_PATTERN = True
        try:
            self.victim.write_read("123 FAil 123")
        except:
            assert True
        else:
            assert False

        self.victim.RAISE_READ_FAIL_PATTERN = False
        assert self.victim.write_read("123 FAil 123").last_output == "123 FAil 123"

    def test__r_all(self):
        assert self.victim._write([f"hello{i}" for i in range(3)]) is True
        assert self.victim.read_lines() == [f"hello{i}" for i in range(3)]

    def test__write_args_kwargs(self):
        assert self.victim.write_read("hello").last_output == "hello"
        assert self.victim.write_read("hello", args=[1, 2]).last_output == "hello 1 2"
        assert self.victim.write_read("hello", kwargs={"CH1": 1}).last_output == "hello CH1=1"
        assert self.victim.write_read("hello", args=[1, 2], kwargs={"CH1": 1}).last_output == "hello 1 2 CH1=1"

    def test__CMD_PREFIX(self):
        self.victim.PREFIX = "DEV:01:"
        assert self.victim.write_read("hello").last_output == f"{self.victim.PREFIX}hello"
        assert self.victim.write_read("hello 12").last_output == f"{self.victim.PREFIX}hello 12"

        self.victim.PREFIX = ""
        assert self.victim.write_read("hello").last_output == "hello"

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
        self.victim.PREFIX = "DEV:01:"
        assert self.victim.hello() == f"{self.victim.PREFIX}hello"
        assert self.victim.hello(12) == f"{self.victim.PREFIX}hello 12"
        self.victim.PREFIX = ""
        assert self.victim.hello() == f"hello"


# =====================================================================================================================
