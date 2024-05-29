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
# @pytest.mark.skip
class Test__ATC:
    victim: SerialClient

    # @classmethod
    # def setup_class(cls):
    #     pass
    #
    # @classmethod
    # def teardown_class(cls):
    #     if cls.victim:
    #         cls.victim.disconnect()
    #
    # def setup_method(self, method):
    #     pass

    def teardown_method(self, method):
        pass
        if self.victim:
            self.victim.disconnect()

    # -----------------------------------------------------------------------------------------------------------------
    def test__1(self):
        class Atc_SerialClient(SerialClient):
            RAISE_CONNECT = False

            # ADDRESS = AddressAutoAcceptVariant.FIRST_FREE__PAIRED_FOR_EMU
            ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__ANSWER_VALID
            # ADDRESS = "COM24"
            # ADDRESS = "/dev/ttyUSB0"
            BAUDRATE = 115200
            PREFIX = "ATC:03:"
            EOL__SEND = b"\r"

            def address__answer_validation(self) -> bool:
                return self.write_read__last_validate("get name", "ATC 03")

        self.victim = Atc_SerialClient()
        assert self.victim.connect()
        print(f"{self.victim.connect()=}")
        # print(f"{self.victim.addresses_system__detect()=}")
        print(f"{self.victim.ADDRESS=}")
        assert self.victim.address_check__resolved()


# =====================================================================================================================
