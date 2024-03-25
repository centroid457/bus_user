# RELEASE HISTORY

********************************************************************************
## TODO
1. add all other port settings into SerialClient  

********************************************************************************
## FIXME
1. ...  

********************************************************************************
## NEWS

0.2.20 (2024/03/25 10:35:41)
------------------------------
- [SerialServer]:  
	- add cmd__exit  

0.2.19 (2024/03/21 14:32:06)
------------------------------
- [SerialClient]:  
	- add CONNECTED  

0.2.18 (2024/03/21 14:19:37)
------------------------------
- [SerialClient]:  
	- rename to _soft_connection  

0.2.17 (2024/03/21 13:11:14)
------------------------------
- [SerialClient]:  
	- add Exx_SerialAddress_AlreadyOpened_InOtherObject  
	- ref connect  

0.2.16 (2024/03/21 12:05:32)
------------------------------
- [SerialServer] add connect__validation  

0.2.15 (2024/03/20 15:50:48)
------------------------------
- [SerialServer] fix extra HELLO_MSG.append(additional_line)  

0.2.14 (2024/03/20 12:20:40)
------------------------------
- [SerialClient] fix emulator disconnect/terminate[Serial] some refs  

0.2.13 (2024/03/20 10:46:02)
------------------------------
- [SerialServer] add cmd__upper/lower  

0.2.12 (2024/03/19 18:21:40)
------------------------------
- [SerialClient] try fix start_emu  

0.2.11 (2024/03/19 16:57:00)
------------------------------
- [SerialClient] separate _EMULATOR__CLS/INST  
- [SerialServer] start add first logger  

0.2.10 (2024/03/19 12:52:46)
------------------------------
- [SerialServer] add connect (fix reconnection)  

0.2.9 (2024/03/19 11:55:33)
------------------------------
- [SerialServer] return back ADDRESS  

0.2.8 (2024/03/19 11:28:44)
------------------------------
- [SerialClient] FIX connect! add param _dont_start_emu  
- [SerialServer]:  
	- add SerialServer_Echo  
	- FIX ADDRESS usage!  
- [SerialDerivatives] add SerialClient_Shorted/SerialClient_Emulated  

0.2.7 (2024/03/18 15:15:51)
------------------------------
- zero add tests RECONNECT  

0.2.6 (2024/03/18 14:53:07)
------------------------------
- [SerialClient] add _EMULATOR_START  

0.2.5 (2024/03/15 11:05:32)
------------------------------
- [SerialServer] zero place EMULATOR.ADDRESS.FIRST_FREE__PAIRED_FOR_EMU  

0.2.4 (2024/03/15 10:45:47)
------------------------------
- [SerialClient] zero + clear Emulator buffer on connection  

0.2.3 (2024/03/14 19:41:42)
------------------------------
- [SerialClient]:  
	- ref to FIRST_FREE__PAIRED_FOR_EMU  
	- add Emulator into it!!!  
- [SerialServer_Base] add HELLO_MSG__SEND_ON_START  

0.2.2 (2024/03/14 16:53:05)
------------------------------
- [SerialClient] renames + add addresses_shorted__detect/*count  

0.2.1 (2024/03/14 15:03:50)
------------------------------
- [SerialClient] place all important lists ADDRESSES__SYSTEM/PAIRED into base class(SerialClient)! so you can use AddressAutoAcceptVariant.FIRST_PAIRED_0/1 in server!!!  

0.2.0 (2024/03/14 14:46:27)
------------------------------
- [SerialClient] BIG REF:  
	- ref address as TYPE__ADDRESS with autoconnect  
	- add lists ADDRESSES__SYSTEM/PAIRED  
	- [AddressAutoAcceptVariant] add FIRST_SHORTED + FIRST_PAIRED_0/1  

0.1.13 (2024/03/13 16:17:31)
------------------------------
- [SerialClient] fix autodetect = switching to already opened  

0.1.12 (2024/03/13 15:58:51)
------------------------------
- [SerialClient] fix autodetect  

0.1.11 (2024/03/11 11:22:41)
------------------------------
- [SerialClient] handle BackSpace send manually from terminal  

0.1.10 (2024/03/06 17:02:29)
------------------------------
- [SerialClient] address__autodetect_logic = apply Exx as False  

0.1.9 (2024/03/06 16:46:22)
------------------------------
- [SerialServer] Value_FromVariants = apply comparing objects by str()  

0.1.8 (2024/03/06 15:45:15)
------------------------------
- [SerialClient] separate AddressAutoAcceptVariant inn class +add AUTODETECT by func  

0.1.7 (2024/03/05 16:59:07)
------------------------------
- [SerialServer] fix _LIST__HELP - show structure with certainty Units/Variants  

0.1.6 (2024/03/05 16:37:26)
------------------------------
- [SerialServer/CMDs] no need params (like line_parsed as before)  

0.1.5 (2024/03/05 15:58:33)
------------------------------
- [SerialServer] add list_results  

0.1.4 (2024/03/05 14:40:05)
------------------------------
- [SerialServer] from CMD NONE is equivalent for SUCCESS  

0.1.3 (2024/03/05 13:42:36)
------------------------------
- [SerialServer] add Value_WithUnit/Value_FromVariants/Value_NotPassed  

0.1.2 (2024/03/04 15:37:29)
------------------------------
- add Value_WithUnit for SerialServer  

0.1.1 (2024/03/04 11:01:41)
------------------------------
- SerialServer:  
	- add tests NoConnection  
	- finish path/list in set/get param and all working logic  

0.1.0 (2024/02/28 15:59:21)
------------------------------
- add SerialServer (need tests)  

0.0.5 (2024/01/31 11:45:56)
------------------------------
- add write_read_line_last  

0.0.4 (2024/01/26 15:31:19)
------------------------------
- just apply new pypi template 0.0.2  

0.0.3 (2023-12-14)
-------------------
- add BusI2c (just simple for detect_i2c_devices/*buses)
- return only HistoryIO from write_read_line

0.0.2 (2023-12-13)
-------------------
- add history class

0.0.1 (2023-12-12)
-------------------
- first SerialClient with commands mapping

********************************************************************************
