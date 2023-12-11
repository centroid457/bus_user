import pathlib
import sys
import glob
from typing import *

from serial import Serial, SerialException
from serial.tools import list_ports

from object_info import ObjectInfo


# =====================================================================================================================
class Exx_SerialAddressInaccessible(Exception):
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
class SerialPort:
    ADDRESS: str = None
    TIMEOUT: float = 0.2
    RAISE: bool = True

    _source: Optional[Serial] = None

    def __init__(self, address: Optional[str] = None):
        if address is not None:
            self.ADDRESS = address

    def connect(self, address: Optional[str] = None, _raise: Optional[bool] = None) -> Union[bool, NoReturn]:
        self._source = None

        if address is None:
            address = self.ADDRESS
        if _raise is None:
            _raise = self.RAISE

        try:
            self._source = Serial(port=address, timeout=self.TIMEOUT)
        except:
            msg = f"[WARN] not accessible {address=}/{self.TIMEOUT=}"
            print(msg)
            self.detect_available_ports()

            if _raise:
                raise Exx_SerialAddressInaccessible(msg)
            else:
                return False

        msg = f"[OK] connected {address=}/{self.TIMEOUT=}"
        print(msg)
        return True

    def read_line(self):
        pass

    @classmethod
    def detect_available_ports(cls) -> List[str]:
        result = cls._detect_available_ports_1__standard_method()
        for port in cls._detect_available_ports_2__direct_access():
            if port not in result:
                result.append(port)

        # result -------------------------------------------------------
        if result:
            print(f"[OK] detected ports {result}")
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
        """Определяет список НЕОТКРЫТЫХ портов - способом 2 (слепым тестом подключения).
        Всегда срабатывает!
        """
        lock_port = None
        lock_port = Serial(port="COM6", timeout=5)

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
        exceptions: Set[Exception] = set()
        for name in attempt_list:
            try:
                port_attempt = Serial(name)
                port_attempt.close()
                result.append(name)
                print(f"{name} DETECTED SERIAL PORT")

            except Exception as exx:
                # FIXME: FINISH IT!!!
                if "FileNotFoundError" in exx:
                    exceptions.update({exx})
                # except (OSError, SerialException, ):
                print(f"\t{name} incorrect port while detecting")

        if exceptions:
            for exx in exceptions:
                print(f"{exx!r}")

        if lock_port:
            lock_port.close()
        return result


# =====================================================================================================================
if __name__ == "__main__":
    ports = SerialPort.detect_available_ports()
    obj = SerialPort(address=ports[0])
    obj.connect()


# =====================================================================================================================
