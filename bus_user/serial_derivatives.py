from typing import *

from . import SerialClient, Type__AddressAutoAcceptVariant
from .serial_server import SerialServer_Base, SerialServer_Example


# =====================================================================================================================
class SerialClient_Emulated(SerialClient):
    address = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED
    _EMULATOR__CLS = SerialServer_Example
    _EMULATOR__START = True


# =====================================================================================================================
class SerialClient_FirstFree(SerialClient):
    _ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE


class SerialClient_FirstFree_Shorted(SerialClient):
    _ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED


class SerialClient_FirstFree_Paired(SerialClient):
    _ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED


class SerialClient_FirstFree_AnswerValid(SerialClient):
    _ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__ANSWER_VALID


# =====================================================================================================================
