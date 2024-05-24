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
class Test__Paired:
    Victim: Type[SerialClient]
    victim: SerialClient

    @classmethod
    def setup_class(cls):
        print(SerialClient.addresses_paired__detect())

        class Victim(SerialClient):
            LOG_ENABLE = True

            ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED_FOR_EMU
            # def address__answer_validation(self) -> Union[bool, NoReturn]:
            #     return self.write_read_line_last("echo") == "echo"

        cls.Victim = Victim
        cls.victim = cls.Victim()
        if not cls.victim.connect():
            msg = f"[ERROR] not found PORT paired"
            print(msg)
            raise Exception(msg)

    @classmethod
    def teardown_class(cls):
        if cls.victim:
            cls.victim.disconnect()

    def setup_method(self, method):
        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED_FOR_EMU
        self.victim.connect()

    def teardown_method(self, method):
        pass
        if self.victim:
            self.victim.disconnect()

    # -----------------------------------------------------------------------------------------------------------------
    def test__ADDRESS__PAIRED(self):
        # self.victim.disconnect()

        assert self.victim.addresses_paired__count() > 0    # HERE YOU NEED CONNECT/CREATE/COMMUTATE ONE PAIR!
        print(f"{self.victim.ADDRESSES__PAIRED=}")

        assert self.victim.connect() is True

        addr_paired = self.victim.address_paired__get()
        assert addr_paired is not None

        victim_pair = SerialClient(addr_paired)
        assert victim_pair.connect()

        assert self.victim._write_line("LOAD1")
        assert victim_pair.read_line() == "LOAD1"

        assert victim_pair._write_line("LOAD2")
        assert self.victim.read_line() == "LOAD2"


# =====================================================================================================================
