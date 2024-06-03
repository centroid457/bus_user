from typing import *


from .serial_client import SerialClient, Type__AddressAutoAcceptVariant
from .serial_server import SerialServer_Base, SerialServer_Example


# =====================================================================================================================
class SerialClient_Shorted(SerialClient):
    address = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED


class SerialClient_Emulated(SerialClient):
    address = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED
    _EMULATOR__CLS = SerialServer_Example
    _EMULATOR__START = True


# =====================================================================================================================
