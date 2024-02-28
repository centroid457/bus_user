import pathlib
import re
import sys
import glob
import time
from typing import *
from enum import Enum, auto

from serial import Serial
from serial.tools import list_ports

from object_info import ObjectInfo

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


class Exx_SerialAddress_AlreadyOpened(Exception):
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


class Exx_SerialPL2303IncorrectDriver(Exception):
    """
    REASON
    ======
    typical for windows

    SOLVATION
    ===========
    install last drivers
    manually select other more OLD driver in manager (see from PC)
        version 3.3.2.105/27.10.2008 - is good!
        version 3.8.22.0/22.02.2023 - is not good!!!
    """
    MARKER: str = "PL2303HXA PHASED OUT SINCE 2012. PLEASE CONTACT YOUR SUPPLIER"


# =====================================================================================================================
TYPE__RW_ANSWER = Union[None, str, List[str]]


class TypeWrReturn(Enum):
    ALL_OUTPUT = auto()
    HISTORY_IO = auto()
    DICT = auto()


# =====================================================================================================================
class SerialClient:
    # TODO: use thread!???
    # SETTINGS ------------------------------------------------
    ADDRESS_APPLY_FIRST_VACANT: Optional[bool] = None
    ADDRESS: str = None

    _TIMEOUT__READ_FIRST: float = 0.9       # 0.2 is too short!!! dont touch! in case of reading char by char 0.5 is the best!!! 0.3 is not enough!!!
    # need NONE NOT 0!!! if wait always!!
    # _TIMEOUT__READ_LAST: float = 0.9
    # _TIMEOUT__WRITE: float = 0.5
    BAUDRATE: int = 9600        # 115200

    CMDS_DUMP: List[str] = []   # ["IDN", "ADR", "REV", "VIN", ]
    RAISE_CONNECT: bool = True
    RAISE_READ_FAIL_PATTERN: bool = False
    ENCODING: str = "utf8"
    EOL__SEND: bytes = b"\r\n"      # "\r"=ENTER in PUTTY  but "\r\n"=is better in read Putty!
    EOL__UNI_SET: bytes = b"\r\n"

    CMD_PREFIX: Optional[str] = None

    # TODO: come up and apply ANSWER_SUCCESS??? may be not need cause of redundant
    ANSWER_SUCCESS: str = "OK"  # case insensitive
    ANSWER_FAIL_PATTERN: Union[str, List[str]] = [r".*FAIL.*", ]   # case insensitive!

    _GETATTR_STARTSWITH__SEND: str = "send__"

    # AUX -----------------------------------------------------
    history: HistoryIO = None
    _SERIAL: Serial

    def __init__(self, address: Optional[str] = None):
        super().__init__()
        self._SERIAL = Serial()
        self.history = HistoryIO()

        # set only address!!!
        if address:
            self.ADDRESS = address

        # apply settings
        # self._SERIAL.interCharTimeout = 0.8
        self._SERIAL.baudrate = self.BAUDRATE
        self._SERIAL.timeout = None
        # self._SERIAL.timeout = self._TIMEOUT__READ_FIRST
        # self._SERIAL.write_timeout = self._TIMEOUT__WRITE

    def __del__(self):
        self.disconnect()

    # MSG =============================================================================================================
    def msg_log(self, msg: str = None) -> None:
        msg = f"[{self._SERIAL.port}]{msg}"
        print(msg)

    # CONNECT =========================================================================================================
    def disconnect(self) -> None:
        self._SERIAL.close()

    def connect(
            self,
            address: Optional[str] = None,
            _raise: Optional[bool] = None,
            _silent: Optional[bool] = None
    ) -> Union[bool, NoReturn]:
        msg = None
        exx = None

        # SETTINGS ---------------------------------
        if _raise is None:
            _raise = self.RAISE_CONNECT

        if self._SERIAL.is_open:
            return True

        address = address or self.ADDRESS
        if not address:
            if self.ADDRESS_APPLY_FIRST_VACANT:
                ports = self.system_ports__detect()
                if not ports:
                    msg = f"[ERROR] PORTS NO ONE IN SYSTEM"
                    exx = Exx_SerialAddress_NotExists(msg)

                else:
                    for address in ports:
                        if self.connect(address=address, _raise=False):
                            return True

                    msg = Exx_SerialAddresses_NoVacant
                    exx = Exx_SerialAddresses_NoVacant()
            else:
                msg = Exx_SerialAddress_NotConfigured
                exx = Exx_SerialAddress_NotConfigured()
        else:
            # WORK ---------------------------------
            self._SERIAL.port = address
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

        # FINISH --------------------------------------
        if exx:
            if not _silent:
                self.msg_log(msg)

            if _raise:
                raise exx
            else:
                return False

        if not _silent:
            msg = f"[OK] connected {self._SERIAL}"
            self.msg_log(msg)

        self.cmd_prefix__set()
        # ObjectInfo(self._SERIAL, log_iter=True).print()
        # exit()
        self._clear_buffer_read()
        return True

    def cmd_prefix__set(self) -> None:
        """
        OVERWRITE IF NEED/USED!
        """
        # self.CMD_PREFIX = ""
        return

    def _clear_buffer_read(self) -> None:
        try:
            self.read_lines(_timeout=0.3)
        except:
            pass

    # DETECT PORTS ====================================================================================================
    def address_check_exists(self) -> bool:
        try:
            self.connect(_raise=True, _silent=True)
            self.disconnect()
        except Exx_SerialAddress_NotExists:
            return False
        except:
            return False
        return True

    @classmethod
    def system_ports__detect(cls) -> List[str]:
        result = cls._system_ports__detect_1__standard_method()
        for port in cls._system_ports__detect_2__direct_access():
            if port not in result:
                result.append(port)

        # result -------------------------------------------------------
        if result:
            print(f"[OK] detected serial ports {result}")
        else:
            print("[WARN] detected no serial ports")

        cls.addresses = result
        return result

    @staticmethod
    def _system_ports__detect_1__standard_method() -> Union[List[str], NoReturn]:
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
            result.append(obj.name)
            if Exx_SerialPL2303IncorrectDriver.MARKER in str(obj):
                msg = f'[WARN] incorrect driver [{Exx_SerialPL2303IncorrectDriver.MARKER}]'
                print(msg)
                raise Exx_SerialPL2303IncorrectDriver(msg)
        return result

    @staticmethod
    def _system_ports__detect_2__direct_access() -> Union[List[str], NoReturn]:
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
            if SerialClient(address=name).address_check_exists():
                result.append(name)

        if _lock_port:
            _lock_port.close()
        return result

    @classmethod
    def system_ports__count(cls) -> int:
        return len(cls.system_ports__detect())

    # RW ==============================================================================================================
    pass

    # SUCCESS ---------------------------------------------------------------------------------------------------------
    def answer_is_success(self, data: AnyStr) -> bool:
        data = self._data_ensure_string(data)
        return self.ANSWER_SUCCESS.upper() == data.upper()

    def answer_is_fail(self, data: AnyStr, _raise: Optional[bool] = None) -> Union[bool, NoReturn]:
        if _raise is None:
            _raise = self.RAISE_READ_FAIL_PATTERN

        data = self._data_ensure_string(data)
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

    # EOL__SEND -------------------------------------------------------------------------------------------------------
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

    # BYTES/STR -------------------------------------------------------------------------------------------------------
    @classmethod
    def _data_ensure_bytes(cls, data: AnyStr) -> bytes:
        if isinstance(data, bytes):
            return data
        else:
            return bytes(data, encoding=cls.ENCODING)

    @classmethod
    def _data_ensure_string(cls, data: AnyStr) -> str:
        if isinstance(data, bytes):
            return data.decode(encoding=cls.ENCODING)
        else:
            return str(data)

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

        self._SERIAL.timeout = _timeout or self._TIMEOUT__READ_FIRST or None
        while True:
            new_char = self._SERIAL.readline(1)
            if not new_char:
                # print(f"detected finish line")
                break
            if new_char in self.EOL__UNI_SET:
                eol_received = True
                if data:
                    break
                else:
                    continue

            data += new_char
            # if data:
            #     self._SERIAL.timeout = _timeout or self._TIMEOUT__READ_LAST or None

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

        data = self._bytes_eol__clear(data)
        data = self._data_ensure_string(data)
        self.history.add_output(data)
        self.answer_is_fail(data)
        return data

    def _write_line(self, data: Union[AnyStr, List[AnyStr]], args: Optional[List] = None, kwargs: Optional[Dict] = None) -> bool:
        """
        just send data into bus!
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
                    if not self._write_line(data_i):
                        return False
                return True
            else:
                data = data[0]

        # SINGLE ---------------------
        data = self._create_cmd_line(data, *args, **kwargs)
        self.history.add_input(self._data_ensure_string(data))

        data = self._data_ensure_bytes(data)
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
                history_i = self.write_read_line(data_i)
                history.add_history(history_i)
        else:
            # SINGLE LAST -----------------------
            data_o = ""
            if self._write_line(data=data, args=args, kwargs=kwargs):
                data_o = self.read_lines()
            history.add_io(self._data_ensure_string(data), data_o)

        # RESULT ----------------------------
        return history

    def write_read_line_last(
            self,
            data: Union[AnyStr, List[AnyStr]],
            args: Optional[List] = None,
            kwargs: Optional[Dict] = None,
    ) -> Union[str, NoReturn]:
        """
        it is created specially for single cmd usage! but decided leave multy cmd usage as feature.
        return always last_output
        """
        return self.write_read_line(data=data, args=args, kwargs=kwargs).last_output

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
    def _create_cmd_line(self, cmd: Any, *args, **kwargs) -> str:
        result = ""

        cmd = str(cmd)

        if self.CMD_PREFIX and not cmd.startswith(self.CMD_PREFIX):
            result += f"{self.CMD_PREFIX}"

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
        return lambda *args, **kwargs: self.write_read_line_last(data=self._create_cmd_line(item, *args, **kwargs))


# =====================================================================================================================
if __name__ == "__main__":
    # see/use tests
    # ports = SerialClient.detect_available_ports()
    # obj = SerialClient(address=ports[0])
    # obj.connect()
    pass


# =====================================================================================================================
