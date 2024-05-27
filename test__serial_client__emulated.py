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
class Test__Emulated:
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

    # def setup_method(self, method):
    #     pass
    #     # self.victim.connect(_raise=False)
    #
    # def teardown_method(self, method):
    #     pass
    #     # if self.victim:
    #     #     self.victim.disconnect()

    # -----------------------------------------------------------------------------------------------------------------
    def test__reconnect(self):
        assert self.victim.check__connected() is True
        assert self.victim._EMULATOR__INST.SERIAL_CLIENT.check__connected() is True

        assert self.victim._EMULATOR__INST.isRunning() is True
        assert self.victim.write_read_line_last("echo 123") == "echo 123"

        self.victim.disconnect()
        assert self.victim.check__connected() is False
        assert self.victim._EMULATOR__INST.SERIAL_CLIENT.check__connected() is False

        assert self.victim._EMULATOR__INST.isRunning() is False

        self.victim.connect()
        assert self.victim.check__connected() is True
        assert self.victim._EMULATOR__INST.SERIAL_CLIENT.check__connected() is True

        assert self.victim._EMULATOR__INST.isRunning() is True
        assert self.victim.write_read_line_last("echo 123") == "echo 123"

    @pytest.mark.skip
    def test__old(self):
        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED
        self.victim._EMULATOR__INST = SerialServer_Base()
        self.victim._EMULATOR__START = True

        assert self.victim._EMULATOR__INST.isRunning() is False
        assert self.victim.connect(_raise=False)
        assert self.victim._EMULATOR__INST.isRunning() is True

        assert self.victim.ADDRESS == self.victim.ADDRESSES__PAIRED[0][0]
        assert self.victim.ADDRESS == self.victim.addresses_paired__get_used()[0]

        assert self.victim._EMULATOR__INST.SERIAL_CLIENT.ADDRESS == self.victim.ADDRESSES__PAIRED[0][1]
        assert self.victim._EMULATOR__INST.SERIAL_CLIENT.ADDRESS == self.victim.addresses_paired__get_used()[1]

        assert self.victim.write_read_line_last("echo 123") == "echo 123"

        assert self.victim._write_line("echo 123")
        assert self.victim.read_line(_timeout=1) == "echo 123"

        # RECONNECT ----------------
        self.victim.disconnect()

        assert self.victim._EMULATOR__INST.isRunning() is False
        assert self.victim.connect(_raise=False)
        assert self.victim._EMULATOR__INST.isRunning() is True

        assert self.victim.write_read_line_last("echo 123") == "echo 123"


# =====================================================================================================================
