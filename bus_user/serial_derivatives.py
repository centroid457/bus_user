from typing import *

from bus_user import SerialClient, Type__AddressAutoAcceptVariant
from .serial_server import SerialServer_Base, SerialServer_Example


# =====================================================================================================================
class SerialClient_FirstFree(SerialClient):
    _ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE

    def address_forget(self) -> None:
        """
        see BaseCls!
        """
        self.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE

class SerialClient_FirstFree_Shorted(SerialClient):
    _ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED

    def address_forget(self) -> None:
        """
        see BaseCls!
        """
        self.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED


class SerialClient_FirstFree_Paired(SerialClient):
    _ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED

    def address_forget(self) -> None:
        """
        see BaseCls!
        """
        self.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED


class SerialClient_FirstFree_AnswerValid(SerialClient):
    _ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__ANSWER_VALID

    def address_forget(self) -> None:
        """
        see BaseCls!
        """
        self.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__ANSWER_VALID


# =====================================================================================================================
class SerialClient_Emulated(SerialClient_FirstFree_Paired):
    _EMULATOR__CLS = SerialServer_Example
    _EMULATOR__START = True


# =====================================================================================================================
if __name__ == '__main__':
    victim = SerialClient_FirstFree_Shorted()
    victim.connect()


# =====================================================================================================================
