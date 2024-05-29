from typing import *
from testplans import DeviceBase
from bus_user import *


# =====================================================================================================================
class Atc_SerialClient(SerialClient):
    RAISE_CONNECT = False

    # ADDRESS = AddressAutoAcceptVariant.FIRST_FREE__PAIRED_FOR_EMU
    ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__ANSWER_VALID
    # ADDRESS = "COM24"
    # ADDRESS = "/dev/ttyUSB0"
    BAUDRATE = 115200
    PREFIX = "ATC:03:"
    EOL__SEND = b"\r"

    # EMULATOR ------------------------
    # _EMULATOR__CLS = Atc_Emulator
    # _EMULATOR__START = True

    def address__answer_validation(self) -> bool:
        return self.write_read_line_last("get name") == "ATC 03"


# =====================================================================================================================
class Device(DeviceBase):
    conn = Atc_SerialClient()


# =====================================================================================================================
def test__1():
    pass
    # emu = Atc_Emulator()
    # emu.start()
    # emu.wait()

    dev = Atc_SerialClient()
    assert dev.connect()
    print(f"{dev.connect()=}")
    # print(f"{dev.addresses_system__detect()=}")
    print(f"{dev.ADDRESS=}")
    assert dev.address_check__resolved()

    #
    # print(f"{dev.address__answer_validation()=}")
    # print(f"{dev.address__answer_validation()=}")
    # print(f"{dev.address__answer_validation()=}")
    #
    # print(f"{dev.write_read_line_last('get name')=}")
    # print(f"{dev.write_read_line_last('get name')=}")
    # print(f"{dev.write_read_line_last('get name')=}")
    # print(f"{dev.write_read_line_last('get name')=}")
    # print(f"{dev.write_read_line_last('get name')=}")
    # print(f"{dev.disconnect()=}")
    # print(f"{dev.ADDRESS=}")


# =====================================================================================================================
