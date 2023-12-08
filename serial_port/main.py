import pathlib
from serial.tools import list_ports
from typing import *

from object_info import ObjectInfo


# =====================================================================================================================


# =====================================================================================================================
class SerialPort:
    @classmethod
    def print(cls) -> None:
        """
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
        """
        port_obj_list = list_ports.comports()

        if port_obj_list:
            ObjectInfo(port_obj_list[0]).print(hide_skipped=True, hide_build_in=True)
        else:
            print("[WARN]no ports found")


# =====================================================================================================================
if __name__ == "__main__":
    SerialPort.print()


# =====================================================================================================================
