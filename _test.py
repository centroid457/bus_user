import os
import pytest
import pathlib
import shutil
from tempfile import TemporaryDirectory
from typing import *
from configparser import ConfigParser

from bus_user import *


# =====================================================================================================================
class Test_BusSerial:
    VICTIM: Type[BusSerial] = type("VICTIM", (BusSerial,), {})

    @classmethod
    def setup_class(cls):
        ports = cls.VICTIM.detect_available_ports()
        if len(ports) != 1:
            msg = f"[ERROR] need connect only one SerialPort and short Rx+Tx"
            print(msg)
            raise Exception(msg)

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        self.VICTIM = type("VICTIM", (BusSerial,), {})

    # -----------------------------------------------------------------------------------------------------------------
    def test__detect_available_ports(self):
        ports = self.VICTIM.detect_available_ports()
        assert len(ports) > 0

    def test__connect(self):
        ports = self.VICTIM.detect_available_ports()
        obj = BusSerial(address=ports[0])
        assert obj.connect() is True


# =====================================================================================================================
