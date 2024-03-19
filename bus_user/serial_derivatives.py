from typing import *


from .serial_client import SerialClient, AddressAutoAcceptVariant
from .serial_server import SerialServer_Base, SerialServer_Example


# =====================================================================================================================
class SerialClient_Shorted(SerialClient):
    ADDRESS = AddressAutoAcceptVariant.FIRST_FREE__SHORTED


class SerialClient_Emulated(SerialClient):
    ADDRESS = AddressAutoAcceptVariant.FIRST_FREE__PAIRED_FOR_EMU
    _EMULATOR = SerialServer_Example()
    _EMULATOR_START = True


# =====================================================================================================================
