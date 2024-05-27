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
class Test__WithUnit:
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
class Test__FromVariants:
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

