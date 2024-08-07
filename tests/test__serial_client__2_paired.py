import pytest
from typing import *
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

            _ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED
            # def address__validate(self) -> Union[bool, NoReturn]:
            #     return self.write_read_line_last("echo") == "echo"

        cls.Victim = Victim
        cls.victim = cls.Victim()
        if not cls.victim.connect():
            msg = f"[ERROR] not found PORT paired"
            print(msg)
            raise Exception(msg)

    # @classmethod
    # def teardown_class(cls):
    #     if cls.victim:
    #         cls.victim.disconnect()
    #
    # def setup_method(self, method):
    #     self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED
    #     self.victim.connect()

    def teardown_method(self, method):
        pass
        if self.victim:
            self.victim._addresses__release()
            self.victim.disconnect()

    # -----------------------------------------------------------------------------------------------------------------
    def test__ADDRESS__PAIRED(self):
        # self.victim.disconnect()

        assert self.victim.addresses_paired__count() > 0    # HERE YOU NEED CONNECT/CREATE/COMMUTATE ONE PAIR!
        print(f"{self.victim.ADDRESSES__PAIRED=}")

        assert self.victim.connect() is True

        addr_paired = self.victim.address_paired__get()
        assert addr_paired is not None

        victim_pair = SerialClient()
        assert victim_pair.connect(address=addr_paired)

        assert self.victim._write("LOAD1")
        assert victim_pair.read_line() == "LOAD1"

        assert victim_pair._write("LOAD2")
        assert self.victim.read_line() == "LOAD2"


# =====================================================================================================================
