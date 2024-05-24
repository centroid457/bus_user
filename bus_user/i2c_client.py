# REQUIREMENTS ========================================================================================================
# decide what to do with it!!!
from requirements_checker import ReqCheckStr_Os
ReqCheckStr_Os.raise_if__WINDOWS()


# IMPORT ==============================================================================================================
from typing import *
import re
from smbus2 import SMBus

from object_info import ObjectInfo
from cli_user import CliUser


# =====================================================================================================================
class Exx_I2cConnection(Exception):
    pass


# =====================================================================================================================
class Patterns:
    I2C_BUS_ID: str = r"i2c-(\d+)\s"
    I2C_DEVICES: str = r"(?=\s([0-9a-f]{2})\s)"


# =====================================================================================================================
class BusI2c:
    BUS_ID: Optional[int] = None
    ADDRESS: Optional[int] = None

    def __int__(self, bus_id: Optional[int] = None, address: Optional[int] = None):
        if bus_id is not None:
            self.BUS_ID = bus_id
        if address is not None:
            self.ADDRESS = address

        # just print available!
        self.detect_i2c_devices()

    @classmethod
    def detect_i2c_buses(cls) -> List[int]:
        """
        EXPLORE
        =======
            string = '''
            i2c-1   i2c             bcm2835 (i2c@7e804000)                  I2C adapter
            i2c-2   i2c             bcm2835 (i2c@7e805000)                  I2C adapter
            '''
            buses = re.findall(pattern=r"i2c-(\\d+) ", string=string)
            print(f"found {buses=}")
        """
        cli = CliUser()
        cli.send("i2cdetect -l")
        buses = re.findall(pattern=Patterns.I2C_BUS_ID, string=cli.last_stdout)
        print(f"found {buses=}")
        return list(map(int, buses))

    @classmethod
    def detect_i2c_devices(cls, bus_id: Optional[int] = None) -> Dict[int, List[int]]:
        """
        EXPLORE
        =======
            string = '''
                 0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
            00:                         -- -- -- -- -- -- -- --
            10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
            20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
            30: -- -- -- -- -- -- -- -- 38 -- 3a 3b -- -- -- --
            40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
            50: 50 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
            60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
            70: -- -- -- -- -- -- -- --
            '''
            devices = re.findall(pattern=r"(?= ([0-9a-f]{2}) )", string=string)
            print(f"found {devices=}")      # found devices=['38', '3a', '3b', '50']
        """
        if bus_id is None:
            buses = cls.detect_i2c_buses()
        elif isinstance(bus_id, (list, tuple, )):
            buses = bus_id
        else:
            buses = [bus_id, ]

        cli = CliUser()
        bus_devices: Dict[int, List[int]] = {}
        for bus in buses:
            cli.send(f"i2cdetect -y {bus}")
            devices = re.findall(pattern=Patterns.I2C_DEVICES, string=cli.last_stdout)
            devices = list(map(lambda value: int(value, 16), devices))
            print(f"I2C: on {bus=} found {devices=}")
            bus_devices.update({bus: devices})

        return bus_devices


# =====================================================================================================================
