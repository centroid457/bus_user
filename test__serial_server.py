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
    def test__cmd__script(self):
        victim = self.Victim()
        assert victim._cmd__(LineParsed("script1")) == AnswerVariants.ERR__NAME_CMD_OR_PARAM
        assert victim._cmd__(LineParsed("script script1")) == AnswerVariants.SUCCESS

    def test__LISTS(self):
        victim = self.Victim()
        assert set(victim._LIST__CMDS) == {
            "set", "get",
            "hello", "help", "echo",
            "upper", "lower",

            "cmd", "cmd_no_line",

            "script",
        }
        assert set(victim._LIST__SCRIPTS) == {
            "script1",
        }

    def test__cmd__cmd(self):
        victim = self.Victim()
        assert victim._cmd__(LineParsed("cmd")) == AnswerVariants.SUCCESS
        assert victim._cmd__(LineParsed("cmd_no_line")) == AnswerVariants.SUCCESS

    def test__cmd__echo(self):
        victim = self.Victim()
        assert victim._cmd__(LineParsed("echo 123")) == "echo 123"
        assert victim._cmd__(LineParsed("echo HELLO")) == "echo HELLO"

    def test__cmd__upper_lower(self):
        victim = self.Victim()
        assert victim._cmd__(LineParsed("upper HELLO")) == "UPPER HELLO"
        assert victim._cmd__(LineParsed("lower HELLO")) == "lower hello"

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

        victim.PARAMS["VAR"] = 1
        assert victim.PARAMS["VAR"] == 1
        assert victim._cmd__(LineParsed("var=11 int=16")) == AnswerVariants.SUCCESS
        assert victim.PARAMS["VAR"] == 11
        assert victim.PARAMS["INT"] == 16

        # NOCHANGES if wrong name exists
        assert victim._cmd__(LineParsed("var=110 int123=160")) == AnswerVariants.ERR__NAME_CMD_OR_PARAM
        assert victim.PARAMS["VAR"] == 11
        assert victim.PARAMS["INT"] == 16

    def test__Value_WithUnit(self):
        victim = self.Victim()
        victim.PARAMS["UNIT123"] = Value_WithUnit(1, unit="V")
        assert victim.PARAMS["UNIT123"] == Value_WithUnit(1, unit="V")
        assert victim._cmd__(LineParsed("unit123")) == "1V"

        assert victim._cmd__(LineParsed("unit123=11")) == AnswerVariants.SUCCESS
        assert victim._cmd__(LineParsed("unit123")) == "11V"

        assert victim._cmd__(LineParsed("unit123=1.00")) == AnswerVariants.SUCCESS
        assert victim._cmd__(LineParsed("unit123")) == "1.0V"

        assert victim.PARAMS["UNIT123"] == Value_WithUnit(1.0, unit="V")

    def test__Value_FromVariants(self):
        victim = self.Victim()

        victim.PARAMS["VARIANT"] = Value_FromVariants(220, variants=[220, 380])
        assert victim._cmd__(LineParsed("variant")) == "220"

        assert victim._cmd__(LineParsed("variant=11")) == AnswerVariants.ERR__VALUE_INCOMPATIBLE
        assert victim._cmd__(LineParsed("variant")) == "220"

        assert victim._cmd__(LineParsed("variant=380")) == AnswerVariants.SUCCESS
        assert victim._cmd__(LineParsed("variant")) == "380"

        assert victim.PARAMS["VARIANT"] == Value_FromVariants(380, variants=[220, 380])

    def test__list_results(self):
        victim = self.Victim()
        victim.PARAMS["VARIANT"] = Value_FromVariants(220, variants=[220, 380])
        victim.PARAMS["UNIT123"] = Value_WithUnit(1, unit="V")

        assert victim.list_param_results(["VARIANT", "UNIT123"]) == ["VARIANT=220", "UNIT123=1V"]
        assert victim.list_param_results(["cmd", "unit123"]) == [f"cmd={AnswerVariants.SUCCESS}", "unit123=1V"]


# =====================================================================================================================
class Test_SerialServer_WithConnection:
    Victim: Type[SerialClient] = type("Victim", (SerialClient,), {})
    victim: SerialClient = None

    @classmethod
    def setup_class(cls):
        if cls.Victim.addresses_paired__count() < 1:
            msg = f"[ERROR] need connect TWO SerialPorts"
            print(msg)
            raise Exception(msg)

        cls.Victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED_FOR_EMU
        cls.Victim._EMULATOR__CLS = SerialServer_Example
        cls.Victim._EMULATOR__START = True

        cls.victim = cls.Victim()
        cls.victim.connect()

    @classmethod
    def teardown_class(cls):
        if cls.victim:
            cls.victim.disconnect()

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    def test__1(self):
        assert self.victim.write_read_line("hello").list_output() == self.victim._EMULATOR__INST.HELLO_MSG
        assert self.victim.write_read_line_last("echo 123") == "echo 123"
        assert self.victim.write_read_line_last("CMD_NOT_ESISTS") == AnswerVariants.ERR__NAME_CMD_OR_PARAM
        assert self.victim.write_read_line_last("upper hello") == "UPPER HELLO"


# =====================================================================================================================
class Test_SerialServer_WithConnection__CONN_VALIDATION:
    @classmethod
    def setup_class(cls):
        class Victim(SerialClient):
            def connect__validation(self) -> bool:
                return self.UPPER("hello") == "UPPER HELLO"

        cls.Victim = Victim

        if cls.Victim.addresses_paired__count() < 1:
            msg = f"[ERROR] need connect TWO SerialPorts"
            print(msg)
            raise Exception(msg)

        cls.Victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED_FOR_EMU
        cls.Victim._EMULATOR__CLS = SerialServer_Example
        cls.Victim._EMULATOR__START = True

        cls.victim = cls.Victim()
        cls.victim.connect()

    @classmethod
    def teardown_class(cls):
        if cls.victim:
            cls.victim.disconnect()

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    def test__1(self):
        assert self.victim.write_read_line("hello").list_output() == self.victim._EMULATOR__INST.HELLO_MSG
        assert self.victim.write_read_line_last("echo 123") == "echo 123"
        assert self.victim.write_read_line_last("CMD_NOT_ESISTS") == AnswerVariants.ERR__NAME_CMD_OR_PARAM
        # assert self.victim.write_read_line_last("upper hello") == "UPPER HELLO"


# =====================================================================================================================
