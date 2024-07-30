import pytest
from typing import *
from bus_user import *


# =====================================================================================================================
JUST_LOAD = "JUST_LOAD"


# =====================================================================================================================
class Test__Shorted_AddressResolved:
    Victim: Type[SerialClient]
    victim: SerialClient

    @classmethod
    def setup_class(cls):
        class Victim(SerialClient_FirstFree_Shorted):
            RAISE_CONNECT = False

        cls.Victim = Victim

    # @classmethod
    # def teardown_class(cls):
    #     pass
    #
    # def setup_method(self, method):
    #     pass
    #
    def teardown_method(self, method):
        pass
        if self.victim:
            self.victim.disconnect()

    # -----------------------------------------------------------------------------------------------------------------
    def test__address_check__resolved(self):
        self.victim = self.Victim()
        assert self.victim.address_check__resolved() is False
        assert self.victim.connect() is True
        assert self.victim.address_check__resolved() is True
        self.victim.disconnect()
        assert self.victim.address_check__resolved() is True

        self.victim.ADDRESS = None
        assert self.victim.address_check__resolved() is False

        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED
        assert self.victim.address_check__resolved() is False
        assert self.victim.connect() is True
        assert self.victim.address_check__resolved() is True

    # -----------------------------------------------------------------------------------------------------------------
    def test__ADDRESSES(self):
        self.victim = self.Victim()
        print(self.victim.addresses_system__detect())
        assert self.victim.address_check__resolved() is False
        assert len(set(self.victim.addresses_system__detect().values())) == 1
        assert self.victim.connect() is True
        assert self.victim.connect() is True
        print(self.victim.addresses_system__detect())
        assert self.victim.address_check__resolved() is True
        ports_owners_set = set(self.victim.addresses_system__detect().values())
        if len(ports_owners_set) == 2:
            assert True
        else:
            assert None not in ports_owners_set
        self.victim.disconnect()


# =====================================================================================================================
class Test__Shorted_Connect:
    Victim: Type[SerialClient]
    victim: SerialClient

    @classmethod
    def setup_class(cls):
        class Victim(SerialClient_FirstFree_Shorted):
            def address__answer_validation(self):       # this is only for FIRST_FREE__ANSWER_VALID! not for FIRST_FREE__SHORTED and etc!
                return self._address__answer_validation__shorted()

        cls.Victim = Victim
        cls.victim = cls.Victim()
        cls.victim._addresses__release()
        if not cls.victim.connect():
            msg = f"[ERROR] not found PORT shorted by Rx+Tx"
            print(msg)
            raise Exception(msg)

    @classmethod
    def teardown_class(cls):
        if cls.victim:
            cls.victim.disconnect()

    def setup_method(self, method):
        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED
        self.victim.connect(_raise=False)

    def teardown_method(self, method):
        pass
        if self.victim:
            # self.victim.address__release()
            self.victim.disconnect()

    # ADDRESS ---------------------------------------------------------------------------------------------------------
    def test__addresses_detect_available(self):
        assert self.Victim.addresses_system__count() > 0

    def test__address_NOTexisted(self):
        assert SerialClient.address__check_exists(address="HELLO") is False

    # AUTOCONNECT -----------------------------------------------------------------------------------------------------
    def test__ADDRESS__FIRST_VACANT(self):
        self.victim.disconnect()

        self.victim.ADDRESS = None
        assert not self.victim.connect(_raise=False)

        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE
        assert self.victim.connect(_raise=False)

        assert isinstance(self.victim.ADDRESS, str)

    def test__ADDRESS__FIRST_SHORTED(self):
        self.victim.disconnect()

        self.victim.ADDRESS = None
        assert not self.victim.connect(_raise=False)

        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED
        assert self.victim.connect(_raise=False)
        assert self.victim.addresses_shorted__count() > 0

    def test__ADDRESS__FIRST_ANSWER_VALID(self):
        self.victim.disconnect()

        self.victim.ADDRESS = None
        assert not self.victim.connect(_raise=False)

        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__ANSWER_VALID
        assert self.victim.connect(_raise=False)

        # ==============
        self.victim.disconnect()
        class Victim(SerialClient):
            _ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__ANSWER_VALID
            def address__answer_validation(self) -> Union[bool, NoReturn]:
                raise Exception()

        assert not Victim().connect(_raise=False)

    # CONNECT ---------------------------------------------------------------------------------------------------------
    def test__connect_multy(self):
        assert self.victim.connect(_raise=False)
        assert self.victim.connect(_raise=False)
        assert self.victim.connect(_raise=False)

    def test__recreate_object(self):
        self.victim.disconnect()

        self.victim = self.Victim()
        assert self.victim.connect(_raise=False)
        assert self.victim.write_read__last_validate(JUST_LOAD, JUST_LOAD)

        self.victim.disconnect()
        self.victim = self.Victim()
        self.victim.connect(_raise=False)
        assert self.victim.write_read__last_validate(JUST_LOAD, JUST_LOAD)
        self.victim.disconnect()

    def test__connect_if_addr_resolved(self):
        self.victim.disconnect()

        assert self.victim.connect() is True
        assert self.victim.connect__only_if_address_resolved() is True

        self.victim.ADDRESS = None
        assert self.victim.connect(_raise=False) is False
        assert self.victim.connect__only_if_address_resolved() is None

        self.victim.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED
        assert self.victim.connect__only_if_address_resolved() is None
        assert self.victim.connect() is True
        assert self.victim.connect__only_if_address_resolved() is True


# =====================================================================================================================
class Test__Shorted_Base:
    Victim: Type[SerialClient_FirstFree_Shorted]
    victim: SerialClient_FirstFree_Shorted

    @classmethod
    def setup_class(cls):
        cls.Victim = SerialClient_FirstFree_Shorted
        cls.victim = cls.Victim()
        if not cls.victim.connect():
            msg = f"[ERROR] not found PORT shorted by Rx+Tx"
            print(msg)
            raise Exception(msg)

    @classmethod
    def teardown_class(cls):
        if cls.victim:
            cls.victim.disconnect()

    # def setup_method(self, method):
    #     pass
    #
    # def teardown_method(self, method):
    #     pass


# =====================================================================================================================
class Test__Shorted_WR(Test__Shorted_Base):
    def test__wr_single(self):
        assert self.victim.connect(_raise=False)
        assert self.victim._write("") is True
        assert self.victim.read_lines() == []

        assert self.victim._write("hello") is True
        assert self.victim.read_lines() == ["hello", ]
        assert self.victim.read_lines() == []

    def test__wr_multy(self):
        # RW single ----------------------
        for line in range(3):
            assert self.victim._write(f"hello{line}") is True

        for line in range(3):
            assert self.victim.read_line() == f"hello{line}"
        assert self.victim.read_lines() == []

        # W list ----------------------
        assert self.victim._write([f"hello{line}" for line in range(3)]) is True
        for line in range(3):
            assert self.victim.read_line() == f"hello{line}"
        assert self.victim.read_lines() == []

        # R list ----------------------
        assert self.victim._write([f"hello{line}" for line in range(3)]) is True
        assert self.victim.read_lines() == [f"hello{line}" for line in range(3)]

        assert self.victim._write([f"hello{line}" for line in range(3)]) is True
        assert self.victim.read_lines() == [f"hello{line}" for line in range(3)]

    def test__wr(self):
        assert self.victim.write_read("hello").last_output == "hello"
        assert self.victim.write_read([f"hello{line}" for line in range(3)]).list_output() == [f"hello{line}" for line in range(3)]

        # params -----------------------
        assert self.victim.write_read("hello").as_dict() == {"hello": ["hello", ], }

        assert self.victim.write_read(["11", "22"]).list_input() == ["11", "22"]
        assert self.victim.write_read(["11", "22"]).as_dict() == {"11": ["11", ], "22": ["22", ], }

        history = HistoryIO()
        history.add_io("hello", "hello")
        assert self.victim.write_read("hello").as_dict() == history.as_dict()
        assert history.check_equal_io() is True

        history = HistoryIO()
        history.add_io("11", "11")
        history.add_io("22", "22")
        assert self.victim.write_read(["11", "22"]).as_dict() == history.as_dict()
        assert history.check_equal_io() is True

    def test__wr_last(self):
        assert self.victim.write_read__last("hello") == "hello"
        assert self.victim.write_read__last(["hello1", "hello2"]) == "hello2"

    def test__wr_last_validate(self):
        assert self.victim.write_read__last_validate("hello", "hello")
        assert self.victim.write_read__last_validate(["hello1", "hello2"],  "hello2")
        assert self.victim.write_read__last_validate(["hello1", "hello2"],  "HELLO2")   # CASE

        assert not self.victim.write_read__last_validate(["hello1", "hello2"],  "hello333")

        assert not self.victim.write_read__last_validate(["hello1", "hello2"],  ["hello333", ])
        assert not self.victim.write_read__last_validate(["hello1", "hello2"],  ["hello333", 'hello1'])
        assert self.victim.write_read__last_validate(["hello1", "hello2"],  ["hello333", 'hello2'])

    def test__wr_last_validate_regexp(self):
        assert self.victim.write_read__last_validate_regexp("hello", "hello") is True
        assert self.victim.write_read__last_validate_regexp("hello", "he.*") is True
        assert self.victim.write_read__last_validate_regexp("hello", ["he.*", ]) is True
        assert self.victim.write_read__last_validate_regexp("hello", ["HE.*", ]) is True
        assert self.victim.write_read__last_validate_regexp("hello", ["hello123", ]) is False
        assert self.victim.write_read__last_validate_regexp("hello", ["hello123", "HELLO"]) is True

    def test__wr_ReadFailPattern(self):
        self.victim.RAISE_READ_FAIL_PATTERN = True
        try:
            self.victim.write_read("123 FAil 123")
        except:
            assert True
        else:
            assert False

        self.victim.RAISE_READ_FAIL_PATTERN = False
        assert self.victim.write_read("123 FAil 123").last_output == "123 FAil 123"

    def test__r_all(self):
        assert self.victim._write([f"hello{i}" for i in range(3)]) is True
        assert self.victim.read_lines() == [f"hello{i}" for i in range(3)]

    def test__write_args_kwargs(self):
        assert self.victim.write_read("hello").last_output == "hello"
        assert self.victim.write_read("hello", args=[1, 2]).last_output == "hello 1 2"
        assert self.victim.write_read("hello", kwargs={"CH1": 1}).last_output == "hello CH1=1"
        assert self.victim.write_read("hello", args=[1, 2], kwargs={"CH1": 1}).last_output == "hello 1 2 CH1=1"

    def test__CMD_PREFIX(self):
        self.victim.PREFIX = "DEV:01:"
        assert self.victim.write_read("hello").last_output == f"{self.victim.PREFIX}hello"
        assert self.victim.write_read("hello 12").last_output == f"{self.victim.PREFIX}hello 12"

        self.victim.PREFIX = ""
        assert self.victim.write_read("hello").last_output == "hello"


# =====================================================================================================================
class Test__Shorted_WR_Getattr(Test__Shorted_Base):
    def test__getattr__1_STARTSWITH(self):
        assert self.victim.send__hello() == "hello"

    def test__getattr__2_cmd_direct(self):
        assert self.victim.hello() == "hello"
        assert self.victim.hello(12) == "hello 12"
        assert self.victim.hello(12, 13) == "hello 12 13"
        assert self.victim.hello("12 13") == "hello 12 13"
        assert self.victim.hello(CH1=12, CH2=13) == "hello CH1=12 CH2=13"
        assert self.victim.hello("?") == "hello ?"

        assert self.victim.hello(12, kwarg1=1) == "hello 12 kwarg1=1"
        assert self.victim.send__hello(12, kwarg1=1) == "hello 12 kwarg1=1"

    def test__getattr__3_cmd_w_args(self):
        assert self.victim.hello__11() == "hello 11"
        assert self.victim.hello__11__22() == "hello 11 22"
        assert self.victim.hello__11__22(33) == "hello 11 22 33"
        assert self.victim.hello__11__22(33, 44, kwarg1=1, kwarg2=2) == "hello 11 22 33 44 kwarg1=1 kwarg2=2"

        assert self.victim.send__hello__11__22(33, 44, kwarg1=1, kwarg2=2) == "hello 11 22 33 44 kwarg1=1 kwarg2=2"

    def test__getattr__0_PREFIX(self):
        self.victim.PREFIX = "DEV:01:"
        assert self.victim.hello() == f"{self.victim.PREFIX}hello"
        assert self.victim.hello(12) == f"{self.victim.PREFIX}hello 12"
        self.victim.PREFIX = ""
        assert self.victim.hello() == f"hello"


# =====================================================================================================================
class Test__Shorted_WR_ValueUnit(Test__Shorted_Base):
    def test__1(self):
        assert self.victim.send__123() == "123"
        assert self.victim.send__123() == 123
        assert self.victim.send__123() > 122
        assert self.victim.send__123() < 123.1

        assert self.victim.send__123v() > 122
        assert self.victim.send__123v() + 1 == 124


# =====================================================================================================================
