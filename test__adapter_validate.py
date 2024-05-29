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
    """
    VALIDATE ADAPTERS fro DECODУ ERRORS
    """
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
    @pytest.mark.skip
    def test__shorted(self):
        """
        connect shorted port and start this code!
        wait for first error and see the step number
        write as result in SerialClient docstring
        """
        # PREPARE ------------------------
        class Victim(SerialClient):
            ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED

        self.victim = Victim()
        if not self.victim.connect():
            msg = f"[ERROR] not found PORT shorted by Rx+Tx"
            print(msg)
            raise Exception(msg)

        # START WORKING ------------------
        index = 0
        while True:
            index += 1
            load = f"step {index}"
            print(load)
            assert self.victim.write_read_line_last(load) == load

    # @pytest.mark.skip
    def test__real_device(self):    # TODO: fix it!!!
        """
        in case of validate real device like ATC/PTB
        DONT FORGET TO CHANGE address__answer_validation for your device!!!
        """
        # PREPARE ------------------------
        VALIDATION_CMD, VALIDATION_ANSWER = ("GET NAME", "ATC 03")

        class Victim(SerialClient):
            ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__ANSWER_VALID

            def address__answer_validation(self) -> bool:
                answer = self.write_read_line_last(VALIDATION_CMD)
                print(f"[{self._SERIAL.port}]{answer=}")
                return answer == VALIDATION_ANSWER

        self.victim = Victim()
        if not self.victim.connect():
            msg = f"[ERROR] not found PORT validated"
            print(msg)
            raise Exception(msg)

        # START WORKING ------------------
        index = 0
        while True:
            index += 1
            load = f"step {index}"
            print(load)
            assert self.victim.address__answer_validation() is True


# =====================================================================================================================
