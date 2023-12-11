import pathlib
import sys
import glob
from typing import *

from serial import Serial
from serial.tools import list_ports

from object_info import ObjectInfo


# =====================================================================================================================
class Exx_SerialAddressNotConfigured(Exception):
    """
        raise SerialException("Port must be configured before it can be used.")
    serial.serialutil.SerialException: Port must be configured before it can be used.
    """
    pass


class Exx_SerialAddressNotExists(Exception):
    """
    SerialException("could not open port 'COM6': FileNotFoundError(2, 'Не удается найти указанный файл.', None, 2)") - всегда несуществующий порт в Windows!!!
    """
    pass


class Exx_SerialAddressAlreadyOpened(Exception):
    """
    SerialException("could not open port 'COM7': PermissionError(13, 'Отказано в доступе.', None, 5)")
    """
    pass


class Exx_SerialAddressOtherError(Exception):
    """
    SerialException("could not open port 'COM7': OSError(22, 'Указано несуществующее устройство.', None, 433)") - порт есть, но получена ошибка при открытии!!!
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
class BusSerial:
    ADDRESS: str = None
    TIMEOUT: float = 0.2
    RAISE: bool = True
    ENCODING: str = "utf-8"
    EOL: bytes = b"\n"

    _source: Serial = Serial()

    def __init__(self, address: Optional[str] = None):
        if address is not None:
            self.ADDRESS = address

    def __del__(self):
        self.disconnect()

    def address_check_exists(self) -> bool:
        try:
            self.connect(_raise=True, _silent=True)
            self.disconnect()
        except Exx_SerialAddressNotExists:
            return False
        return True

    # CONNECT =========================================================================================================
    def disconnect(self) -> None:
        self._source.close()

    def connect(self, address: Optional[str] = None, _raise: Optional[bool] = None, _silent: Optional[bool] = None) -> Union[bool, NoReturn]:
        if address is None:
            address = self.ADDRESS
        if _raise is None:
            _raise = self.RAISE

        self._source.port = address
        self._source.timeout = self.TIMEOUT

        try:
            self._source.open()
        except Exception as exx:
            if not _silent:
                print(f"{exx!r}")

            if "FileNotFoundError" in str(exx):
                msg = f"[ERROR] PORT NOT EXISTS IN SYSTEM {self._source}"
                exx = Exx_SerialAddressNotExists(repr(exx))

                # self.detect_available_ports()

            elif "Port must be configured before" in str(exx):
                msg = f"[ERROR] PORT NOT CONFIGURED {self._source}"
                exx = Exx_SerialAddressNotConfigured(repr(exx))

            elif "PermissionError" in str(exx):
                msg = f"[ERROR] PORT ALREADY OPENED {self._source}"
                exx = Exx_SerialAddressAlreadyOpened(repr(exx))

            else:
                msg = f"[ERROR] PORT OTHER ERROR {self._source}"
                exx = Exx_SerialAddressOtherError(repr(exx))

            if not _silent:
                print(msg)

            if _raise:
                raise exx
            else:
                return False

        if not _silent:
            msg = f"[OK] connected {self._source}"
            print(msg)
        return True

    # DETECT PORTS ====================================================================================================
    @classmethod
    def detect_available_ports(cls) -> List[str]:
        result = cls._detect_available_ports_1__standard_method()
        for port in cls._detect_available_ports_2__direct_access():
            if port not in result:
                result.append(port)

        # result -------------------------------------------------------
        if result:
            print(f"[OK] detected serial ports {result}")
        else:
            print("[WARN] detected no serial ports")
        return result

    @staticmethod
    def _detect_available_ports_1__standard_method():
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
            ObjectInfo(obj).print(hide_skipped=True, hide_build_in=True)
            result.append(obj.name)
            if Exx_SerialPL2303IncorrectDriver.MARKER in str(obj):
                msg = f'[WARN] incorrect driver [{Exx_SerialPL2303IncorrectDriver.MARKER}]'
                print(msg)
                raise Exx_SerialPL2303IncorrectDriver(msg)
        return result

    @staticmethod
    def _detect_available_ports_2__direct_access() -> Union[List[str], NoReturn]:
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
            raise EnvironmentError('Unsupported platform')

        result: List[str] = []
        for name in attempt_list:
            if BusSerial(address=name).address_check_exists():
                result.append(name)

        if _lock_port:
            _lock_port.close()
        return result

    # RW ==============================================================================================================
    pass

    # EOL -------------------------------------------------------------------------------------------------------------
    @classmethod
    def _bytes_eol__ensure(cls, data: bytes) -> bytes:
        if not data.endswith(cls.EOL):
            data = data + cls.EOL
        return data

    @classmethod
    def _bytes_eol__clear(cls, data: bytes) -> bytes:
        while data.endswith(cls.EOL):
            data = data.removesuffix(cls.EOL)
        return data

    # BYTES/STR -------------------------------------------------------------------------------------------------------
    @classmethod
    def _data_ensure_bytes(cls, data: Union[str, bytes]) -> bytes:
        if isinstance(data, bytes):
            return data
        else:
            return bytes(data, encoding=cls.ENCODING)

    @classmethod
    def _data_ensure_string(cls, data: Union[str, bytes]) -> str:
        if isinstance(data, bytes):
            return data.decode(encoding=cls.ENCODING)
        else:
            return str(data)

    # RW --------------------------------------------------------------------------------------------------------------
    # TODO: use wrapper for connect/disconnect!???
    def read_line(self) -> str:
        data = self._source.readline()
        if data:
            print(f"[OK]read_line={data}")
        else:
            print(f"[WARN]BLANK read_line={data}")
        data = self._bytes_eol__clear(data)
        data = self._data_ensure_string(data)
        # print(f"[OK]read_line={data}")
        return data

    def write_line(self, data: Union[str, bytes]) -> bool:
        if not data:
            print(f"[WARN]BLANK write_line={data}")
            return False

        data = self._data_ensure_bytes(data)
        data = self._bytes_eol__ensure(data)
        data_length = self._source.write(data)
        print(f"[OK]write_line={data}/{data_length=}")
        if data_length > 0:
            return True
        else:
            msg = f"[ERROR] data not write"
            print(msg)
            return False


# =====================================================================================================================
if __name__ == "__main__":
    # see/use tests
    # ports = BusSerial.detect_available_ports()
    # obj = BusSerial(address=ports[0])
    # obj.connect()
    pass


# =====================================================================================================================
