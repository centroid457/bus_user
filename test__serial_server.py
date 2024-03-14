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
class Test__Value_WithUnit:
    @classmethod
    def setup_class(cls):
        pass
        cls.Victim = type("Victim", (Value_WithUnit,), {})
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
    def test__str(self):
        victim = self.Victim()
        assert victim.value == 0
        assert victim.UNIT == ""
        assert victim.SEPARATOR == ""
        assert str(victim) == "0"

        victim = self.Victim(1)
        assert victim.value == 1
        assert victim.UNIT == ""
        assert victim.SEPARATOR == ""
        assert str(victim) == "1"

        victim = self.Victim(1, unit="V")
        assert victim.value == 1
        assert victim.UNIT == "V"
        assert victim.SEPARATOR == ""
        assert str(victim) == "1V"

        victim = self.Victim(1, unit="V", separator=" ")
        assert victim.value == 1
        assert victim.UNIT == "V"
        assert victim.SEPARATOR == " "
        assert str(victim) == "1 V"

    def test__cmp__same(self):
        assert self.Victim() == self.Victim()
        assert self.Victim(1, separator=" ") == self.Victim(1, separator="")
        assert self.Victim(1.0) == self.Victim(1)

        assert self.Victim(1) != self.Victim(2)

    def test__cmp__other(self):
        assert self.Victim() == 0
        assert self.Victim(1, separator=" ") == 1
        assert self.Victim(1.0) == 1

        assert self.Victim(1) != 2


# =====================================================================================================================
class Test__Value_FromVariants:
    @classmethod
    def setup_class(cls):
        pass
        cls.Victim = type("Victim", (Value_FromVariants,), {})

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
    def test__case(self):
        victim = self.Victim(value="var1", variants=["VAR1", "VAR2"])
        assert victim.value == "VAR1"
        assert str(victim) == "VAR1"

        try:
            victim = self.Victim(value="var1", variants=["VAR1", "VAR2"], case_insensitive=False)
            assert False
        except:
            pass

    def test__variants_validate(self):
        victim = self.Victim(value="var", variants=["VAR", "var"], case_insensitive=False)
        assert victim.value == "var"

        try:
            victim = self.Victim(value="var123", variants=["VAR", "var"], case_insensitive=False)
            assert False
        except Exx__ValueNotInVariants:
            pass
        except Exception as exx:
            print(f"{exx!r}")
            assert False

        try:
            victim = self.Victim(value="var123", variants=["VAR", "var"], case_insensitive=True)
            assert False
        except Exx__VariantsIncompatible:
            pass
        except Exception as exx:
            print(f"{exx!r}")
            assert False

    def test__types__None(self):
        victim = self.Victim(variants=["NONE", ])
        assert victim.value == Value_NotPassed
        # assert str(victim) == "NONE"

        victim = self.Victim(value=None, variants=["NONE", ])
        assert victim.value == "NONE"
        assert str(victim) == "NONE"

        victim = self.Victim(value="None", variants=[None, ])
        assert victim.value is None
        assert str(victim) == "None"

    def test__types__int(self):
        victim = self.Victim(value=1, variants=["1", ])
        assert victim.value == "1"
        assert str(victim) == "1"

        victim = self.Victim(value="1", variants=[1, ])
        assert victim.value == 1
        assert str(victim) == "1"

    def test__cmp__same_obj(self):
        assert self.Victim(value=None, variants=["NONE", ]) == self.Victim(value="None", variants=["NONE", ])
        assert self.Victim(value="NONE", variants=["NONE", ]) == self.Victim(value="None", variants=["NONE", ])
        assert self.Victim(value=None, variants=["None", ]) == self.Victim(value=None, variants=["NONE", ])

        assert self.Victim(value=None, variants=["None", ], case_insensitive=False) != self.Victim(value=None, variants=["NONE", ])

    def test__cmp__simple_value(self):
        assert self.Victim(value=None, variants=["NONE", ]) == "NONE"
        assert self.Victim(value="NONE", variants=["NONE", ]) == "NONE"
        assert self.Victim(value=None, variants=["None", ]) == "NONE"
        assert self.Victim(value=None, variants=[None, ]) == "NONE"
        assert self.Victim(value=None, variants=[None, ], case_insensitive=False) != "NONE"
        assert self.Victim(value=None, variants=[None, ], case_insensitive=False) == "None"

    def test__contain(self):
        victim = self.Victim(variants=["NONE", ])
        assert None in victim
        assert "None" in victim
        assert "NONE" in victim

    def test__len(self):
        assert len(self.Victim(variants=[0, ])) == 1
        assert len(self.Victim(variants=[0, 1])) == 2

    def test__iter(self):
        assert list(self.Victim(variants=[0, ])) == [0, ]
        assert list(self.Victim(variants=[0, 1])) == [0, 1, ]


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
        assert victim.ORIGINAL == ""
        assert victim.PREFIX == ""
        assert victim.CMD == ""
        assert victim.ARGS == []
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 0

        victim = self.Victim("hello")
        assert victim.ORIGINAL == "hello"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == []
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 0

        victim = self.Victim("HELLO")
        assert victim.ORIGINAL == "HELLO"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == []
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 0

    def test__args_kwargs(self):
        victim = self.Victim("HELLO CH")
        assert victim.ORIGINAL == "HELLO CH"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == ["ch", ]
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 1
        assert victim.KWARGS_count() == 0

        victim = self.Victim("HELLO CH 1")
        assert victim.ORIGINAL == "HELLO CH 1"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == ["ch", "1", ]
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 2
        assert victim.KWARGS_count() == 0

        victim = self.Victim("HELLO CH=1")
        assert victim.ORIGINAL == "HELLO CH=1"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == []
        assert victim.KWARGS == {"ch": "1"}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 1

        victim = self.Victim("HELLO CH1 CH2=2    ch3=3  ch4")
        assert victim.ORIGINAL == "HELLO CH1 CH2=2    ch3=3  ch4"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == ["ch1", "ch4"]
        assert victim.KWARGS == {"ch2": "2", "ch3": "3"}
        assert victim.ARGS_count() == 2
        assert victim.KWARGS_count() == 2

    def test__kwargs_spaces(self):
        victim = self.Victim("CH =  1")
        assert victim.ORIGINAL == "CH =  1"
        assert victim.PREFIX == ""
        assert victim.CMD == ""
        assert victim.ARGS == []
        assert victim.KWARGS == {"ch": "1"}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 1

        victim = self.Victim("hello CH =  1")
        assert victim.ORIGINAL == "hello CH =  1"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == []
        assert victim.KWARGS == {"ch": "1"}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 1

        victim = self.Victim("hello CH ===  1")
        assert victim.ORIGINAL == "hello CH ===  1"
        assert victim.PREFIX == ""
        assert victim.CMD == "hello"
        assert victim.ARGS == []
        assert victim.KWARGS == {"ch": "1"}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 1

    def test__kwargs_only(self):
        victim = self.Victim("CH=1")
        assert victim.ORIGINAL == "CH=1"
        assert victim.PREFIX == ""
        assert victim.CMD == ""
        assert victim.ARGS == []
        assert victim.KWARGS == {"ch": "1"}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 1

        victim = self.Victim("CH=1 ch2=2")
        assert victim.ORIGINAL == "CH=1 ch2=2"
        assert victim.PREFIX == ""
        assert victim.CMD == ""
        assert victim.ARGS == []
        assert victim.KWARGS == {"ch": "1", "ch2": "2"}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 2

    def test__prefix(self):
        victim = self.Victim("HELLO CH 1", _prefix_expected="HELLO")
        assert victim.ORIGINAL == "HELLO CH 1"
        assert victim.PREFIX == "hello"
        assert victim.CMD == "ch"
        assert victim.ARGS == ["1", ]
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 1
        assert victim.KWARGS_count() == 0

        victim = self.Victim("HELLO CH 1", _prefix_expected="HELLO CH 1")
        assert victim.ORIGINAL == "HELLO CH 1"
        assert victim.PREFIX == "hello ch 1"
        assert victim.CMD == ""
        assert victim.ARGS == []
        assert victim.KWARGS == {}
        assert victim.ARGS_count() == 0
        assert victim.KWARGS_count() == 0

        victim = self.Victim("HELLO CH 1", _prefix_expected="HELLO123")
        assert victim.ORIGINAL == "HELLO CH 1"
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

            "cmd", "cmd_no_line"
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

    VictimEmu: Type[SerialServer_Base] = type("VictimEmu", (SerialServer_Base,), {})
    victim_emu: SerialServer_Base = None

    @classmethod
    def setup_class(cls):
        if cls.Victim.addresses_paired__count() < 1:
            msg = f"[ERROR] need connect TWO SerialPorts"
            print(msg)
            raise Exception(msg)

        cls.VictimEmu.ADDRESS = cls.Victim.ADDRESSES__PAIRED[0][0]
        cls.Victim.ADDRESS = cls.Victim.ADDRESSES__PAIRED[0][1]

        cls.victim_emu = cls.VictimEmu()
        cls.victim = cls.Victim()

        cls.victim_emu.start()
        cls.victim.connect()

        time.sleep(0.5)
        cls.victim._clear_buffer_read()

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
        assert self.victim.write_read_line("hello").list_output() == self.victim_emu.HELLO_MSG
        # assert self.victim.write_read_line_last("123") == AnswerVariants.ERR__NAME_CMD_OR_PARAM


# =====================================================================================================================
