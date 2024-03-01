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
class Test__LineParsed:
    @classmethod
    def setup_class(cls):
        pass
        cls.Victim = type("Victim", (LineParsed,), {})

    # @classmethod
    # def teardown_class(cls):
    #     pass
    #
    # def setup_method(self, method):
    #     pass
    #
    # def teardown_method(self, method):
    #     pass

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

    def test__kwargs_spaces(self):
        victim = self.Victim("CH =  1")
        assert victim.LINE == "CH =  1"
        assert victim.PREFIX == ""
        assert victim.CMD == ""
        assert victim.ARGS == []
        assert victim.KWARGS == {"ch": "1"}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 1

        victim = self.Victim("hello CH =  1")
        assert victim.LINE == "hello CH =  1"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == []
        assert victim.KWARGS == {"ch": "1"}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 1

        victim = self.Victim("hello CH ===  1")
        assert victim.LINE == "hello CH ===  1"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == []
        assert victim.KWARGS == {"ch": "1"}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 1

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
class Test__SerialServer_NoConnection:
    # @classmethod
    # def setup_class(cls):
    #     pass
    #
    # @classmethod
    # def teardown_class(cls):
    #     pass
    #
    def setup_method(self, method):
        pass
        self.Victim = type("Victim", (SerialServer_Example,), {})
    #
    # def teardown_method(self, method):
    #     pass
    # -----------------------------------------------------------------------------------------------------------------
    def test__LISTS(self):
        victim = self.Victim()
        assert set(victim._LIST__CMDS) == {
            "set", "get",
            "run",
            "hello", "help", "echo",

            "on",
        }
        assert set(victim._LIST__SCRIPTS) == {
            "script1",
        }

    def test__cmd__cmd(self):
        victim = self.Victim()
        assert victim._cmd__(LineParsed("on")) == AnswerVariants.SUCCESS

    def test__cmd__echo(self):
        victim = self.Victim()
        assert victim._cmd__(LineParsed("echo 123")) == "echo 123"
        assert victim._cmd__(LineParsed("echo HELLO")) == "echo HELLO"

    def test__GET__single(self):
        victim = self.Victim()
        assert victim._cmd__(LineParsed("hello123")) == AnswerVariants.ERR__NAME_CMD_OR_PARAM

        assert victim._cmd__(LineParsed("get str")) == "str"
        assert victim._cmd__(LineParsed("str")) == "str"
        assert victim._cmd__(LineParsed("blanc")) == ""
        assert victim._cmd__(LineParsed("zero")) == '0'

        assert victim._cmd__(LineParsed("int")) == '1'
        assert victim._cmd__(LineParsed("float")) == '1.1'

        assert victim._cmd__(LineParsed("none")) == "None"
        assert victim._cmd__(LineParsed("true")) == "True"
        assert victim._cmd__(LineParsed("false")) == "False"

        try:
            float(victim._cmd__(LineParsed("call")))
        except:
            assert False
        assert victim._cmd__(LineParsed("exx")) == AnswerVariants.ERR__PARAM_CALLING

        assert victim._cmd__(LineParsed("list")) == "[0, 1, 2]"
        assert victim._cmd__(LineParsed("_set")) == "{0, 1, 2}"
        assert victim._cmd__(LineParsed("get _set")) == "{0, 1, 2}"
        assert victim._cmd__(LineParsed("dict_short")) == "{1: 11}"

    def test__GET__nested__list(self):
        victim = self.Victim()
        assert victim._cmd__(LineParsed("list")) == "[0, 1, 2]"

        assert victim._cmd__(LineParsed("list 1")) == "1"
        assert victim._cmd__(LineParsed("list/1")) == "1"

        assert victim._cmd__(LineParsed("get list 1")) == "1"
        assert victim._cmd__(LineParsed("get list/1")) == "1"

        assert victim._cmd__(LineParsed("list/10")) == AnswerVariants.ERR__NAME_CMD_OR_PARAM

        # -----
        assert victim._cmd__(LineParsed("list_2")) == "[[11]]"
        assert victim._cmd__(LineParsed("list_2/0")) == "[11]"
        assert victim._cmd__(LineParsed("list_2/0/0")) == "11"

        assert victim._cmd__(LineParsed("list_2 0 0")) == "11"
        assert victim._cmd__(LineParsed("get list_2 0 0")) == "11"

    def test__GET__dict(self):
        # TODO: add BOOL/NONE
        victim = self.Victim()
        assert victim._cmd__(LineParsed("dict_short_2")) == "{'HEllo': {1: 11}}"
        assert victim._cmd__(LineParsed("get dict_short_2")) == "{'HEllo': {1: 11}}"

        assert victim._cmd__(LineParsed("dict_short_2/hello")) == "{1: 11}"
        assert victim._cmd__(LineParsed("dict_short_2 hello")) == "{1: 11}"
        assert victim._cmd__(LineParsed("get dict_short_2 hello")) == "{1: 11}"
        assert victim._cmd__(LineParsed("dict_short_2/hello11111")) == AnswerVariants.ERR__NAME_CMD_OR_PARAM

        assert victim._cmd__(LineParsed("dict_short_2/hello/1")) == "11"
        assert victim._cmd__(LineParsed("get dict_short_2/hello/1")) == "11"
        assert victim._cmd__(LineParsed("dict_short_2 hello/1")) == "11"
        assert victim._cmd__(LineParsed("get dict_short_2 hello/1")) == "11"
        assert victim._cmd__(LineParsed("dict_short_2 hello 1")) == "11"
        assert victim._cmd__(LineParsed("get dict_short_2 hello 1")) == "11"
        assert victim._cmd__(LineParsed("dict_short_2/hello/11111")) == AnswerVariants.ERR__NAME_CMD_OR_PARAM

        assert victim._cmd__(LineParsed("dict_short_2/hello/1/9/9/9/9/")) == AnswerVariants.ERR__NAME_CMD_OR_PARAM

    def test__SET__level_first__type(self):
        victim = self.Victim()
        assert victim.PARAMS["VAR"] == ''

        assert victim._cmd__(LineParsed("var=True")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] is True

        assert victim._cmd__(LineParsed("var=false")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] is False

        assert victim._cmd__(LineParsed("var=null")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] is None

        assert victim._cmd__(LineParsed("var=")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] == ""

        assert victim._cmd__(LineParsed("var=''")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] == "''"                             # TODO: convert to expected!!!

        assert victim._cmd__(LineParsed("var=0")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] == 0

        assert victim._cmd__(LineParsed("var=123")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] == 123

        assert victim._cmd__(LineParsed("var=1.1")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] == 1.1
        assert victim._cmd__(LineParsed("var=1,1")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] != 1.1

        # ITERABLES --------------------
        assert victim._cmd__(LineParsed("var=[]")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] == []

        # assert victim._cmd__(LineParsed("var=[1, 2]")) == AnswerVariants.SUCCESS  # TODO: CLEAR ALL INTERNAL SPACES!!!
        assert victim._cmd__(LineParsed("var=[1,2]")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] == [1, 2]

    def test__SET__level_first__syntax(self):
        victim = self.Victim()
        assert victim.PARAMS["INT"] == 1

        assert victim._cmd__(LineParsed("set int=10")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["INT"] == 10

        assert victim._cmd__(LineParsed("int=11")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["INT"] == 11

        assert victim._cmd__(LineParsed("int    =12")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["INT"] == 12

        assert victim._cmd__(LineParsed("int=     13")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["INT"] == 13

        assert victim._cmd__(LineParsed("   int       =     14   ")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["INT"] == 14

        assert victim._cmd__(LineParsed("   int =======     15   ")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["INT"] == 15

        # several
        assert victim._cmd__(LineParsed("var 1 int=16")) == AnswerVariants.ERR__ARGS_VALIDATION
        assert victim.PARAMS["INT"] == 15

        assert victim._cmd__(LineParsed("var=11 int=16")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] == 11
        assert victim.PARAMS["INT"] == 16           # FIXME: !!!


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
