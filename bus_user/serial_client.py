import pathlib
import re
import sys
import glob
import time
from typing import *
from enum import Enum, auto

from object_info import ObjectInfo
from logger_aux import Logger

from serial import Serial
from serial.tools import list_ports

from .history import HistoryIO


# =====================================================================================================================
class Exx_SerialAddress_NotConfigured(Exception):
    """
        raise SerialException("Port must be configured before it can be used.")
    serial.serialutil.SerialException: Port must be configured before it can be used.
    """
    pass


class Exx_SerialAddress_NotExists(Exception):
    """
    SerialException("could not open port 'COM6': FileNotFoundError(2, 'Не удается найти указанный файл.', None, 2)") - всегда несуществующий порт в Windows!!!
    """
    pass


class Exx_SerialAddresses_NoVacant(Exception):
    pass


class Exx_SerialAddresses_NoAutodetected(Exception):
    pass


class Exx_SerialAddress_AlreadyOpened(Exception):
    """
    SerialException("could not open port 'COM7': PermissionError(13, 'Отказано в доступе.', None, 5)")
    """
    pass


class Exx_SerialAddress_AlreadyOpened_InOtherObject(Exception):
    """
    SerialException("could not open port 'COM7': PermissionError(13, 'Отказано в доступе.', None, 5)")
    """
    pass


class Exx_SerialAddress_OtherError(Exception):
    """
    SerialException("could not open port 'COM7': OSError(22, 'Указано несуществующее устройство.', None, 433)") - порт есть, но получена ошибка при открытии!!!
    """
    pass


class Exx_SerialRead_NotFullLine(Exception):
    pass


class Exx_SerialRead_FailPattern(Exception):
    """
    if read string which match error pattern
    """
    pass


class Exx_SerialRead_FailDecoding(Exception):
    """
    REASON
    ------
    some serial devices (depends on microchips model) not always give correct reading bytes

    SOLVATION
    ---------
    1. [BESTandONLY] just use other device on other appropriate microchip!
    """


class Exx_SerialPL2303IncorrectDriver(Exception):
    """
    REASON
    ------
    typical for windows

    SOLVATION
    ---------
    1. [BEST] just use other device on other microchip
    2. manually select other more OLD driver in driver/device manager
        version 3.3.2.105/27.10.2008 - is good!
        version 3.8.22.0/22.02.2023 - is not good!!!
    """
    MARKER: str = "PL2303HXA PHASED OUT SINCE 2012. PLEASE CONTACT YOUR SUPPLIER"


# =====================================================================================================================
TYPE__RW_ANSWER = Union[None, str, List[str]]


class Type__WrReturn(Enum):
    ALL_OUTPUT = auto()
    HISTORY_IO = auto()
    DICT = auto()


class Type__AddressAutoAcceptVariant(Enum):
    FIRST_FREE = auto()
    FIRST_FREE__SHORTED = auto()
    FIRST_FREE__ANSWER_VALID = auto()
    FIRST_FREE__PAIRED_FOR_EMU = auto()


TYPE__ADDRESS = Union[None, Type__AddressAutoAcceptVariant, str]


# =====================================================================================================================
class SerialClient(Logger):
    """

    NOTE:
    1. use good COM-port adapters!!!
        some bites may be lost (usually on started byte) or added extra chars (usually to start and end of line)!!!

        DECODING APPROPRIATE MODELS
        ---------------------------
        =WRONG=
        - PROFILIC - often +wrong driver
        - FTDI FT232RL - sometimes but less than on Profilic=fail on step 0/11/20/3 3/9/95!!!
        - CP2102 - fail on step 3392/877/1141/!!! sometimes on step 1715 get SerialTimeoutException

        =GOOD=
        - CH340 - no one error so far!
        - CH341A (big universal) - no one error so far! more then steps about 50 minutes!!! tired of waiting

        =NOT TESTED= wait postage from Aliexpress - already get! need tests!!! use Test__Shorted_validateModel_InfinitRW!!!!
        - CH341T
    """
    pass
    pass
    pass

    # LOGGER --------------------------------------------------
    # LOG_ENABLE = True

    # SETTINGS ------------------------------------------------
    ADDRESS: TYPE__ADDRESS = None

    TIMEOUT__READ: float = 0.3       # 0.2 is too short!!! dont touch! in case of reading char by char 0.5 is the best!!! 0.3 is not enough!!!
    # need NONE NOT 0!!! if wait always!!
    BAUDRATE: int = 9600        # 115200

    CMDS_DUMP: List[str] = []   # ["IDN", "ADR", "REV", "VIN", ]
    RAISE_CONNECT: bool = True
    RAISE_READ_FAIL_PATTERN: bool = False

    PREFIX: Optional[str] = None

    # TODO: come up and apply ANSWER_SUCCESS??? may be not need cause of redundant
    ANSWER_SUCCESS: str = "OK"  # case insensitive
    ANSWER_FAIL_PATTERN: Union[str, List[str]] = [r".*FAIL.*", ]   # case insensitive!

    # rare INFRASTRUCTURE -----------------
    ENCODING: str = "utf8"
    EOL__SEND: bytes = b"\r\n"      # "\r"=ENTER in PUTTY  but "\r\n"=is better in read Putty!
    EOL__UNI_SET: bytes = b"\r\n"

    _GETATTR_STARTSWITH__SEND: str = "send__"

    # test purpose EMULATOR -----------------
    _EMULATOR__CLS: Type['SerialServer_Base'] = None    # IF USED - START it on PAIRED - it is exactly Emulator/Server! no need to use just another serialClient! _EMULATOR__INST could be used for test reason and check values in realtime!!
    _EMULATOR__INST: 'SerialServer_Base' = None
    _EMULATOR__START: bool = None    # DONT DELETE! it need when you reconnecting! cause of ADDRESS replaced after disconnecting by exact str after PAIRED*

    # AUX -----------------------------------------------------
    history: HistoryIO = None
    _SERIAL: Serial

    ADDRESSES__SYSTEM: List[str] = []
    ADDRESSES__SHORTED: List[str] = []
    ADDRESSES__PAIRED: List[Tuple[str, str]] = []

    def __init__(self, address: TYPE__ADDRESS = None):
        super().__init__()
        self._SERIAL = Serial()
        self.history = HistoryIO()

        if self._EMULATOR__CLS:
            self._EMULATOR__INST = self._EMULATOR__CLS()

        # set only address!!!
        if address is not None:
            self.ADDRESS = address

        # apply settings
        # self._SERIAL.interCharTimeout = 0.8
        self._SERIAL.baudrate = self.BAUDRATE
        self._SERIAL.timeout = self.TIMEOUT__READ
        # self._SERIAL.write_timeout = self._TIMEOUT__WRITE

        # self.addresses_system__detect()   # DONT USE in init!!!
        # self.addresses_shorted__detect()   # DONT USE in init!!!
        # self.addresses_paired__detect()   # DONT USE in init!!!

    def __del__(self):
        self.disconnect()

    def address_paired__get(self) -> TYPE__ADDRESS:
        if not self.ADDRESSES__PAIRED:
            self.addresses_paired__detect()

        if not isinstance(self.ADDRESS, str):
            return

        for pair in self.ADDRESSES__PAIRED:
            if self.ADDRESS in pair:
                addr1, addr2 = pair
                if self.ADDRESS == addr1:
                    return addr2
                else:
                    return addr1

    def check__connected(self) -> bool:
        try:
            return self._SERIAL.is_open
        except:
            return False

    # MSG =============================================================================================================
    def msg_log(self, msg: str = None) -> None:
        msg = f"[{self._SERIAL.port}]{msg}"
        print(msg)

    def cmd_prefix__set(self) -> None:
        """
        OVERWRITE IF NEED/USED!
        """
        # self.PREFIX = ""
        return

    def _clear_buffer_read(self) -> None:
        try:
            self.read_lines(_timeout=0.3)
        except:
            pass

    # CONNECT =========================================================================================================
    def disconnect(self) -> None:
        try:
            self._SERIAL.close()
        except:
            pass

        try:
            self._EMULATOR__INST.disconnect()
        except:
            pass

    def connect(
            self,
            address: Optional[str] = None,
            _raise: Optional[bool] = None,
            _silent: Optional[bool] = None,
            _soft_connection: bool = None    # no final connection! specially keep ability to connect without Emu on cls main perpose (search ports)!
    ) -> Union[bool, NoReturn]:
        msg = None
        exx = None

        # SETTINGS ---------------------------------
        if _raise is None:
            _raise = self.RAISE_CONNECT

        address = address or self.ADDRESS

        # AUTOAPPLY ---------------------------------
        if address is None:
            msg = Exx_SerialAddress_NotConfigured
            exx = Exx_SerialAddress_NotConfigured()
        elif address == Type__AddressAutoAcceptVariant.FIRST_FREE:
            return self._address_apply__first_free()
        elif address == Type__AddressAutoAcceptVariant.FIRST_FREE__SHORTED:
            return self._address_apply__first_free__shorted()
        elif address == Type__AddressAutoAcceptVariant.FIRST_FREE__ANSWER_VALID:
            return self._address_apply__first_free__answer_valid()
        elif address == Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED_FOR_EMU:
            return self._address_apply__first_free__paired_for_emu()

        # need_open ==========================================================
        # CHANGE PORT OR USE SAME ---------------------------------
        need_open = True
        if self._SERIAL.port != address:
            if self._SERIAL.is_open:
                self._SERIAL.close()
            self._SERIAL.port = address
            if self._SERIAL.is_open:
                self._SERIAL.port = None
                msg = f"[ERROR] Attempt to connect to already opened port IN OTHER OBJECT {self._SERIAL}"
                exx = Exx_SerialAddress_AlreadyOpened_InOtherObject(msg)

                need_open = False
        else:
            if self._SERIAL.is_open:
                need_open = False

        # Try OPEN ===================================================================
        if need_open:
            try:
                self._SERIAL.open()
            except Exception as _exx:
                if not _silent:
                    self.msg_log(f"{_exx!r}")

                if "FileNotFoundError" in str(_exx):
                    msg = f"[ERROR] PORT NOT EXISTS IN SYSTEM {self._SERIAL}"
                    exx = Exx_SerialAddress_NotExists(repr(_exx))

                    # self.detect_available_ports()

                elif "Port must be configured before" in str(_exx):
                    msg = f"[ERROR] PORT NOT CONFIGURED {self._SERIAL}"
                    exx = Exx_SerialAddress_NotConfigured(repr(_exx))

                elif "PermissionError" in str(_exx):
                    msg = f"[ERROR] PORT ALREADY OPENED {self._SERIAL}"
                    exx = Exx_SerialAddress_AlreadyOpened(repr(_exx))

                else:
                    msg = f"[ERROR] PORT OTHER ERROR {self._SERIAL}"
                    exx = Exx_SerialAddress_OtherError(repr(_exx))

        # FINISH -----------------------------------------------
        # FAIL -----------------------------
        if exx:
            if not _silent:
                self.msg_log(msg)

            if _raise:
                raise exx
            else:
                return False

        # OK -----------------------------
        if not _silent:
            msg = f"[OK] connected {self._SERIAL}"
            self.msg_log(msg)

        self.ADDRESS = self._SERIAL.port

        if not _soft_connection:
            self.emulator_start()
            if not self.connect__validation():
                self.disconnect()
                return False

        self.cmd_prefix__set()
        return True

    def connect__validation(self) -> bool:
        return True

    def emulator_start(self) -> None:
        if self._EMULATOR__INST and self._EMULATOR__START:
            pair_used = self.addresses_paired__get_used()
            if pair_used:
                self._EMULATOR__INST.SERIAL_CLIENT.ADDRESS = pair_used[1]
                self._EMULATOR__INST.connect()
                # self._EMULATOR__INST.wait__cycle_active()
                self._clear_buffer_read()

    # ADDRESS =========================================================================================================
    pass
    pass
    pass
    pass
    pass
    pass
    pass

    def _address_apply__first_free(self) -> bool:
        for address in self.addresses_system__detect():
            if self.connect(address=address, _raise=False):
                return True

        msg = Exx_SerialAddresses_NoVacant
        print(msg)

    def _address_apply__first_free__shorted(self) -> bool:
        """
        dont overwrite! dont mess with address__autodetect_logic!
        used to find exact device in all comport by some special logic like IDN/NAME value
        """
        for address in self.addresses_shorted__detect():
            if self.connect(address=address, _raise=False, _soft_connection=True):
                return True

        # FINISH -------------
        msg = Exx_SerialAddresses_NoAutodetected
        print(msg)

    def _address_apply__first_free__answer_valid(self) -> bool:
        """
        dont overwrite! dont mess with address__autodetect_logic!
        used to find exact device in all comport by some special logic like IDN/NAME value
        """
        for address in self.addresses_system__detect():
            if self.connect(address=address, _raise=False):
                try:
                    if self.address__answer_validation():
                        return True
                except Exception as exx:
                    print(f"finding address {exx!r}")
                    pass
                self.disconnect()

        # FINISH -------------
        msg = Exx_SerialAddresses_NoAutodetected
        print(msg)

    def _address_apply__first_free__paired_for_emu(self) -> bool:
        """
        # FIXME: exists weakness - you need connect at once whole pair!
            if you would use several pairs and delay connecting secondary devices - it will be incorrect pairing!
            may be need using naming pairs! and set pair name with connecting first
            first connects on free port, second connect by pair name??? feels good
        cls.pairs = {
            0: (COM1, COM2),
            1: (COM3, COM4),
        }

        cls.pairs = {
            "ATC": (COM1, COM2),    # change name
            1: (COM3, COM4),
        }
        """
        for addr1, addr2 in self.addresses_paired__detect():
            if self.connect(address=addr1, _raise=False):
                return True

        # FINISH -------------
        msg = Exx_SerialAddresses_NoAutodetected
        print(msg)

    # -----------------------------------------------------------------------------------------------------------------
    def address__answer_validation(self) -> Union[bool, NoReturn]:
        """
        overwrite for you case!
        used to find exact device in all comport by some special logic like IDN/NAME value.

        IDEA:
        1. this func will exec on every accessible address
        2. if this func return True - address would be accepted!
        3. raiseExx/NoReturn - equivalent as False!
        """

    def address__answer_validation__shorted(self) -> Union[bool, NoReturn]:
        load = "EXPECT_ANSWER__SHORTED"
        return self.write_read_line_last(load) == load

    # DETECT PORTS ====================================================================================================
    pass
    pass
    pass
    pass
    pass
    pass
    pass

    def address__check_exists(self) -> bool:
        try:
            self.connect(_raise=True, _silent=True, _soft_connection=True)
            self.disconnect()
        except Exx_SerialAddress_NotExists:
            return False
        except:
            return False
        return True

    @classmethod
    def addresses_system__detect(cls) -> List[str]:
        if SerialClient.ADDRESSES__SYSTEM:
            return SerialClient.ADDRESSES__SYSTEM

        # WORK -------------------------------------------------------
        result = cls._addresses_system__detect_1__standard_method()
        for port in cls._addresses_system__detect_2__direct_access():
            if port not in result:
                result.append(port)

        # result -------------------------------------------------------
        if result:
            print(f"[OK] detected serial ports {result}")
        else:
            print("[WARN] detected no serial ports")

        SerialClient.ADDRESSES__SYSTEM = result
        return result

    @staticmethod
    def _addresses_system__detect_1__standard_method() -> Union[List[str], NoReturn]:
        """
        WINDOWS - USB
            ==========OBJECTINFO.PRINT==========================================================================
            str=COM8 - PL2303HXA PHASED OUT SINCE 2012. PLEASE CONTACT YOUR SUPPLIER.
            repr=<serial.tools.list_ports_common.ListPortInfo object at 0x00000267B3A38200>
            ----------properties_ok-----------------------------------------------------------------------------
            description              	str       :COM8
            device                   	str       :COM8
            hwid                     	str       :USB VID:PID=067B:2303 SER= LOCATION=1-2.4.3
            interface                	NoneType  :None
            location                 	str       :1-2.4.3
            manufacturer             	str       :Prolific
            name                     	str       :COM8
            pid                      	int       :8963
            product                  	NoneType  :None
            serial_number            	str       :
            vid                      	int       :1659
            ----------properties_exx----------------------------------------------------------------------------
            ----------objects-----------------------------------------------------------------------------------
            ----------methods_ok--------------------------------------------------------------------------------
            apply_usb_info           	NoneType  :None
            usb_description          	str       :COM8
            usb_info                 	str       :USB VID:PID=067B:2303 SER= LOCATION=1-2.4.3
            ----------methods_exx-------------------------------------------------------------------------------
            ====================================================================================================

        RASPBERRY - USB
        кажется не видит встроенный COM порт даже после его включения и перезагрузки - только USB!!!

            ==========OBJECTINFO.PRINT==========================================================================
            str=/dev/ttyUSB0 - USB-Serial Controller
            repr=<serial.tools.list_ports_linux.SysFS object at 0x7fb332d9d0>
            ----------properties_ok-----------------------------------------------------------------------------
            description                     str       :USB-Serial Controller
            device                          str       :/dev/ttyUSB0
            device_path                     str       :/sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.4/1-1.4:1.0/ttyUSB0
            hwid                            str       :USB VID:PID=067B:2303 LOCATION=1-1.4
            interface                       NoneType  :None
            location                        str       :1-1.4
            manufacturer                    str       :Prolific Technology Inc.
            name                            str       :ttyUSB0
            pid                             int       :8963
            product                         str       :USB-Serial Controller
            serial_number                   NoneType  :None
            subsystem                       str       :usb-serial
            usb_device_path                 str       :/sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.4
            usb_interface_path              str       :/sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.4/1-1.4:1.0
            vid                             int       :1659
            ----------properties_exx----------------------------------------------------------------------------
            ----------objects-----------------------------------------------------------------------------------
            ----------methods_ok--------------------------------------------------------------------------------
            apply_usb_info                  NoneType  :None
            usb_description                 str       :USB-Serial Controller
            usb_info                        str       :USB VID:PID=067B:2303 LOCATION=1-1.4
            ----------methods_exx-------------------------------------------------------------------------------
            read_line                       TypeError :join() missing 1 required positional argument: 'a'
            ====================================================================================================
        """
        result: List[str] = []

        # find not opened ports ----------------------------------------
        for obj in list_ports.comports():
            # ObjectInfo(obj).print(hide_skipped=True, hide_build_in=True)
            result.append(obj.device)
            if Exx_SerialPL2303IncorrectDriver.MARKER in str(obj):
                msg = f'[WARN] incorrect driver [{Exx_SerialPL2303IncorrectDriver.MARKER}]'
                print(msg)
                raise Exx_SerialPL2303IncorrectDriver(msg)
        return result

    @staticmethod
    def _addresses_system__detect_2__direct_access() -> Union[List[str], NoReturn]:
        """Определяет список портов (НЕОТКРЫТЫХ+ОТКРЫТЫХ!!!) - способом 2 (слепым тестом подключения и анализом исключений)
        Всегда срабатывает!
        """
        _lock_port = None
        # _lock_port = Serial(port="COM7", timeout=5)   # test reason! finding exx already opened!

        if sys.platform.startswith('win'):
            attempt_list = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            attempt_list = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            attempt_list = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('[ERROR]Unsupported platform')

        result: List[str] = []
        for name in attempt_list:
            if SerialClient(address=name).address__check_exists():
                result.append(name)

        if _lock_port:
            _lock_port.close()
        return result

    @classmethod
    def addresses_shorted__detect(cls) -> List[str]:
        if SerialClient.ADDRESSES__SHORTED:
            return SerialClient.ADDRESSES__SHORTED

        # WORK ----------------------------------------------
        result = []
        for address in cls.addresses_system__detect():
            obj = cls()
            if obj.connect(address=address, _raise=False, _soft_connection=True):
                if obj.address__answer_validation__shorted():
                    result.append(address)
                obj.disconnect()

        SerialClient.ADDRESSES__SHORTED = result
        print(f"{cls.ADDRESSES__SHORTED=}")
        return result

    @classmethod
    def addresses_paired__detect(cls) -> list[tuple[str, str]]:
        # print(f"111111{cls.ADDRESSES__PAIRED=}")

        if SerialClient.ADDRESSES__PAIRED:
            return SerialClient.ADDRESSES__PAIRED

        # WORK ----------------------------------------------
        load = "EXPECT_ANSWER__PAIRED"
        result = []
        instances_free = []

        addresses__system = cls.addresses_system__detect()
        for address in addresses__system:
            instance = cls(address)
            if instance.connect(_raise=False, _soft_connection=True):
                instances_free.append(instance)

        while len(instances_free) > 1:
            main = instances_free.pop(0)
            main._write_line(load)
            main.disconnect()

            for index, slave in enumerate(instances_free):
                if slave.read_line(_timeout=0.3) == load:
                    result.append((main.ADDRESS, slave.ADDRESS))
                    slave.disconnect()
                    instances_free.pop(index)
                    break

        for remain in instances_free:
            remain.disconnect()

        cls.ADDRESSES__PAIRED = result
        print(f"{cls.ADDRESSES__PAIRED=}")
        return result

    def addresses_paired__get_used(self) -> Optional[Tuple[str, str]]:
        for pair in self.addresses_paired__detect():
            if self._SERIAL.port in pair:
                return pair

    # COUNTS -----------------------------------------
    @classmethod
    def addresses_system__count(cls) -> int:
        return len(cls.addresses_system__detect())

    @classmethod
    def addresses_shorted__count(cls) -> int:
        return len(cls.addresses_shorted__detect())

    @classmethod
    def addresses_paired__count(cls) -> int:
        return len(cls.addresses_paired__detect())

    # RW ==============================================================================================================
    pass
    pass
    pass
    pass
    pass
    pass
    pass

    # SUCCESS ---------------------------------------------------------------------------------------------------------
    def answer_is_success(self, data: AnyStr) -> bool:
        data = self._data_ensure__string(data)
        return self.ANSWER_SUCCESS.upper() == data.upper()

    def answer_is_fail(self, data: AnyStr, _raise: Optional[bool] = None) -> Union[bool, NoReturn]:
        if _raise is None:
            _raise = self.RAISE_READ_FAIL_PATTERN

        data = self._data_ensure__string(data)
        if isinstance(self.ANSWER_FAIL_PATTERN, str):
            patterns = [self.ANSWER_FAIL_PATTERN, ]
        else:
            patterns = self.ANSWER_FAIL_PATTERN

        for pattern in patterns:
            if re.search(pattern, data, flags=re.IGNORECASE):
                if _raise:
                    msg = f"[ERROR] match fail [{pattern=}/{data=}]"
                    self.msg_log(msg)
                    raise Exx_SerialRead_FailPattern(msg)
                else:
                    return True

        return False

    # BYTES -------------------------------------------------------------------------------------------------------
    @classmethod
    def _bytes_eol__ensure(cls, data: bytes) -> bytes:
        if not data.endswith(cls.EOL__SEND):
            data = data + cls.EOL__SEND
        return data

    @classmethod
    def _bytes_eol__clear(cls, data: bytes) -> bytes:
        while True:
            data_new = data.strip()
            data_new = data_new.strip(cls.EOL__UNI_SET)
            if not data or data == data_new:
                break
            data = data_new
        return data

    @classmethod
    def _bytes_edition__apply(cls, data: bytes) -> bytes:
        """not used so far!!!
        need to handle editions used by hand in manual typing from terminal!
        """
        # TODO: finish or leave blank! its not so necessary!!! and seems a little bit hard to apply
        return data

    # BYTES/STR -------------------------------------------------------------------------------------------------------
    @classmethod
    def _data_ensure__bytes(cls, data: AnyStr) -> bytes:
        if isinstance(data, bytes):
            return data
        else:
            return bytes(data, encoding=cls.ENCODING)

    @classmethod
    def _data_ensure__string(cls, data: AnyStr) -> Union[str, NoReturn]:
        """
        EXCEPTION ORIGINAL VARIANT
        --------------------------
            cls = <class 'test__serial_server.Victim'>, data = b'\x85RR__NAME_CMD_OR_PARAM'

                @classmethod
                def _data_ensure__string(cls, data: AnyStr) -> Union[str, NoReturn]:
                    if isinstance(data, bytes):
            >           return data.decode(encoding=cls.ENCODING)
            E           UnicodeDecodeError: 'utf-8' codec can't decode byte 0x85 in position 0: invalid start byte

            bus_user\serial_client.py:722: UnicodeDecodeError
        """
        try:
            if isinstance(data, bytes):
                return data.decode(encoding=cls.ENCODING)
            else:
                return str(data)
        except Exception as exx:
            print(f"{exx!r}")
            msg = f"[FAIL] decoding {data=}"
            raise Exx_SerialRead_FailDecoding(msg)

    # RW --------------------------------------------------------------------------------------------------------------
    # TODO: use wrapper for connect/disconnect!??? - NO!
    def read_lines(self, _timeout: Optional[float] = None) -> Union[List[str], NoReturn]:
        result: List[str] = []
        while True:
            line = self.read_line(_timeout)
            if line:
                result.append(line)
            else:
                break
        return result

    def read_line(self, _timeout: Optional[float] = None) -> Union[str, NoReturn]:
        """
        read line from bus buffer,
        """
        # FIXME: return Object??? need keep exx for not finished readline!!!
        # var1: just read as usual - could cause error with not full bytes read in ONE CHAR!!!
        # data = self._SERIAL.readline()

        # var2: char by char
        data = b""
        eol_received = False

        self._SERIAL.timeout = _timeout or self.TIMEOUT__READ or None
        while True:
            new_char = self._SERIAL.readline(1)
            if not new_char:
                # print(f"detected finish line")
                break
            if new_char == b'\x7f':     # BACKSPACE
                # LINE EDITION --------------
                data = data[:-1]
                continue

            if new_char in self.EOL__UNI_SET:
                # LINE FINISHED --------------
                eol_received = True
                if data:
                    break
                else:
                    continue

            data += new_char

        # RESULT ----------------------
        if data:
            if not eol_received:
                msg = f"[ERROR]NotFullLine read_line={data}->CLEAR!!!"
                exx = Exx_SerialRead_NotFullLine(msg)
                data = b""
            else:
                msg = f"[OK]read_line={data}"

        else:
            msg = f"[WARN]BLANK read_line={data}"

        if data:
            self.msg_log(msg)

        data = self._bytes_edition__apply(data)
        data = self._bytes_eol__clear(data)
        data = self._data_ensure__string(data)
        self.history.add_output(data)
        self.answer_is_fail(data)
        return data

    def _write_line(
            self,
            data: Union[AnyStr, List[AnyStr]],
            prefix: Optional[str] = None,
            args: Optional[List] = None,
            kwargs: Optional[Dict] = None
    ) -> bool:
        """
        just send data into bus!
        usually we dont need just send without reading! so it useful for debugging

        :return: result of sent

        args/kwargs - used only for single line!!!
        """
        args = args or []
        kwargs = kwargs or {}

        data = data or ""

        # LIST -----------------------
        if isinstance(data, (list, tuple, )):
            if len(data) > 1:
                for data_i in data:
                    if not self._write_line(data=data_i, prefix=prefix, args=args, kwargs=kwargs):
                        return False
                return True
            else:
                data = data[0]

        # SINGLE ---------------------
        data = self._create_cmd_line(cmd=data, prefix=prefix, args=args, kwargs=kwargs)
        self.history.add_input(self._data_ensure__string(data))

        data = self._data_ensure__bytes(data)
        data = self._bytes_eol__ensure(data)

        data_length = self._SERIAL.write(data)
        msg = f"[OK]write_line={data}/{data_length=}"
        self.msg_log(msg)

        if data_length > 0:
            return True
        else:
            msg = f"[ERROR] data not write"
            self.msg_log(msg)
            return False

    def write_read_line(
            self,
            data: Union[AnyStr, List[AnyStr]],
            prefix: Optional[str] = None,
            args: Optional[List] = None,
            kwargs: Optional[Dict] = None,
    ) -> Union[HistoryIO, NoReturn]:
        """
        send data and return history
        """
        history = HistoryIO()

        # LIST -------------------------
        if isinstance(data, (list, tuple,)):
            for data_i in data:
                history_i = self.write_read_line(data_i, prefix=prefix, args=args, kwargs=kwargs)
                history.add_history(history_i)
        else:
            # SINGLE LAST -----------------------
            data_o = ""
            if self._write_line(data=data, prefix=prefix, args=args, kwargs=kwargs):
                data_o = self.read_lines()
            history.add_io(self._data_ensure__string(data), data_o)

        # RESULT ----------------------------
        return history

    def write_read_line_last(
            self,
            data: Union[AnyStr, List[AnyStr]],
            prefix: Optional[str] = None,
            args: Optional[List] = None,
            kwargs: Optional[Dict] = None,
    ) -> Union[str, NoReturn]:
        """
        it is created specially for single cmd usage! but decided leave multy cmd usage as feature.
        return always last_output
        """
        return self.write_read_line(data=data, prefix=prefix, args=args, kwargs=kwargs).last_output

    def dump_cmds(self, cmds: List[str] = None) -> Union[HistoryIO, NoReturn]:
        """
        useful to get results for standard cmds list
        if you need to read all params from device!
        """
        cmds = cmds or self.CMDS_DUMP
        history = self.write_read_line(cmds)
        history.print_io()
        return history

    # CMD =============================================================================================================
    def _create_cmd_line(self, cmd: Any, prefix: Optional[str] = None, args: List[Any] = None, kwargs: Dict[str, Any] = None) -> str:
        result = ""

        cmd = str(cmd)

        if prefix is None:
            prefix = self.PREFIX

        if prefix and not cmd.startswith(prefix):
            result += f"{prefix}"

        result += f"{cmd}"

        if args:
            for arg in args:
                result += f" {arg}"

        if kwargs:
            for name, value in kwargs.items():
                result += f" {name}={value}"
        return result

    # =================================================================================================================
    def __getattr__(self, item: str) -> Callable[..., Union[str, NoReturn]]:
        """if no exists attr/meth

        USAGE COMMANDS MAP
        ==================

        1. SHOW (optional) COMMANDS EXPLICITLY by annotations without values!
        -----------------------------------------------------------------
            class MySerialDevice(SerialClient):
                IDN: Callable[[Any], TYPE__RW_ANSWER]
                ADDR: Callable[[Any], TYPE__RW_ANSWER]
                DUMP: Callable[[Any], TYPE__RW_ANSWER]

        2. USE in code
        --------------
            dev = MySerialDevice()
            dev.connect()
            dev.IDN()   # return answer for sent string in port "IDN"
            dev.VIN()   # return answer for sent string in port "VIN"
            dev.VIN(12)   # return answer for sent string in port "VIN 12"
            dev.VIN("12")   # return answer for sent string in port "VIN 12"
            dev.VIN("12 13")  # return answer for sent string in port "VIN 12 13"
            dev.VIN(12, 13)   # return answer for sent string in port "VIN 12 13" by args
            dev.VIN(CH1=12, CH2=13) # return answer for sent string in port "VIN CH1=12 CH2=13" by kwargs
            dev.VIN(12, CH2=13)     # return answer for sent string in port "VIN 12 CH2=13" by args/kwargs
        """
        if self._GETATTR_STARTSWITH__SEND and item.startswith(self._GETATTR_STARTSWITH__SEND):
            item = item.replace(self._GETATTR_STARTSWITH__SEND, "")
        return lambda *args, **kwargs: self.write_read_line_last(data=self._create_cmd_line(cmd=item, args=args, kwargs=kwargs))


# =====================================================================================================================
if __name__ == "__main__":
    # see/use tests
    # ports = SerialClient.detect_available_ports()
    # obj = SerialClient(address=ports[0])
    # obj.connect()
    pass


# =====================================================================================================================
