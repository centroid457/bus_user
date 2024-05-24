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
@pytest.mark.skip
class Test__Shorted_validateModel_InfinitRW:
    Victim: Type[SerialClient]
    victim: SerialClient

    @classmethod
    def setup_class(cls):
        class Victim(SerialClient):
            ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED

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

    # def setup_method(self, method):
    #     pass
    #
    # def teardown_method(self, method):
    #     pass

    # -----------------------------------------------------------------------------------------------------------------
    def test__1(self):
        index = 0
        while True:
            index += 1
            load = f"echo {index}"
            print(load)
            assert self.victim.write_read_line_last(load) == load


# =====================================================================================================================
