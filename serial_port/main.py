import pathlib
from typing import *

from serial import Serial
from serial.tools import list_ports

from object_info import ObjectInfo


# =====================================================================================================================
class Exx_SerialAddressInaccessible(Exception):
    pass


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
            return True
        except:
            msg = f"[WARN] not accessible {address=}/{self.TIMEOUT=}"
            print(msg)
            self.print()

            if _raise:
                raise Exx_SerialAddressInaccessible(msg)
            else:
                return False

    def read_line(self):
        pass

    @classmethod
    def print(cls) -> None:
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
        port_obj_list = list_ports.comports()

        if port_obj_list:
            ObjectInfo(port_obj_list[0]).print(hide_skipped=True, hide_build_in=True)
        else:
            print("[WARN] no serial ports found")


# =====================================================================================================================
if __name__ == "__main__":
    SerialPort.print()


# =====================================================================================================================
