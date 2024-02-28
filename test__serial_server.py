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
@pytest.mark.skip
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
