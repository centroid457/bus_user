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
class Test__SerialClient_Emulated:
    Victim: Type[SerialClient_Emulated]
    victim: SerialClient_Emulated

    @classmethod
    def setup_class(cls):
        class Victim(SerialClient_Emulated):
            pass

        cls.Victim = Victim
        cls.victim = cls.Victim()
        if not cls.victim.connect(_raise=False):
            msg = f"[ERROR] not found PORT PAIRED"
            print(msg)
            raise Exception(msg)

    @classmethod
    def teardown_class(cls):
        if cls.victim:
            cls.victim.disconnect()

    def setup_method(self, method):
        pass
        # self.victim.connect(_raise=False)

    def teardown_method(self, method):
        pass
        # if self.victim:
        #     self.victim.disconnect()

    # -----------------------------------------------------------------------------------------------------------------
    def test__reconnect(self):
        assert self.victim.CONNECTED is True
        assert self.victim._EMULATOR__INST.SERIAL_CLIENT.CONNECTED is True

        assert self.victim._EMULATOR__INST.isRunning() is True
        assert self.victim.write_read_line_last("echo 123") == "echo 123"

        self.victim.disconnect()
        assert self.victim.CONNECTED is False
        assert self.victim._EMULATOR__INST.SERIAL_CLIENT.CONNECTED is False

        assert self.victim._EMULATOR__INST.isRunning() is False

        self.victim.connect()
        assert self.victim.CONNECTED is True
        assert self.victim._EMULATOR__INST.SERIAL_CLIENT.CONNECTED is True

        assert self.victim._EMULATOR__INST.isRunning() is True
        assert self.victim.write_read_line_last("echo 123") == "echo 123"


# =====================================================================================================================
