# RELEASE HISTORY

********************************************************************************
## TODO
1. add all other port settings into SerialClient  
2. fix all tests! fix EMU  

********************************************************************************
## FIXME
1. ...  

********************************************************************************
## NEWS

0.4.16 (2024/10/01 17:58:56)
------------------------------
- [SerialClient.writeReadLast*] fix timeoutRead on only first read! after first char timeout set default  

0.4.15 (2024/10/01 13:04:41)
------------------------------
- [SerialClient] fix timeoutRead handling+make kwargs for methods over getattr  

0.4.14 (2024/09/27 13:14:19)
------------------------------
- [SerialClient] ref write_read__last_validate make available validators Valid/ValueUbit/ValueVariants  

0.4.13 (2024/09/19 18:12:08)
------------------------------
- [serialClient] zero fix+docstr  

0.4.12 (2024/09/18 17:46:58)
------------------------------
- [serialClient]:  
	- fix good working with not so good adapters, add REWRITEIF_READNOANSWER/*READFAILDECODE/*NOVALID  
	- fix _data_ensure__string with correct comparing elements with printable ascii  
	- fix buffers_clear*/write_eol  

0.4.11 (2024/08/08 14:49:01)
------------------------------
- [serialClient] separate address_resolve from connect as direct meth  

0.4.10 (2024/07/31 17:20:42)
------------------------------
- [SerialClient] fix _addresses__release  

0.4.9 (2024/07/31 17:02:56)
------------------------------
- [SerialClient] zero regrouping methods  

0.4.8 (2024/07/31 16:43:48)
------------------------------
- [SerialClient] fix prev version! there were broken tests  

0.4.7 (2024/07/31 16:04:55)
------------------------------
- [SerialClient] add address_forget  

0.4.6 (2024/07/31 15:16:09)
------------------------------
- [SerialClient] add RELEASE_ON_DISCONNECT  

0.4.5 (2024/07/31 12:23:34)
------------------------------
- [SerialClient] [SerialClient] make occupation as forever! not released on disconnection  

0.4.4 (2024/07/30 14:42:01)
------------------------------
- [SerialServer] mark tests/comments for VlueUnit/Variants are not working  
- [SerialClient] fix ADDRESSES__SYSTEM owners  

0.4.3 (2024/07/30 13:06:55)
------------------------------
- [SerialClient] fix ADDRESSES__SYSTEM owners  

0.4.2 (2024/07/29 14:00:05)
------------------------------
- [ValueUnit/Variants] apply new names  

0.4.1 (2024/07/17 13:10:35)
------------------------------
- [serialClient] fix strings cmp with ValueUnit  

0.4.0 (2024/07/16 15:39:10)
------------------------------
- [serialClient] apply ValueUnit in Answers  
- [pypiTemplate] apply latest  

0.3.17 (2024/06/11 15:03:01)
------------------------------
- [serialClient] add connect__only_if_address_resolved  

0.3.16 (2024/06/11 11:55:29)
------------------------------
- [serialClient] add ability to use args in getattr name  

0.3.15 (2024/06/04 18:09:00)
------------------------------
- [serialClient] zero fix connect  

0.3.14 (2024/06/04 12:54:11)
------------------------------
- [serialClient]:  
	- use only kwargs in init!!!  

0.3.13 (2024/06/04 11:48:05)
------------------------------
- [serialClient]:  
	- zero fix _address__occupy  

0.3.12 (2024/06/04 11:39:23)
------------------------------
- [serialClient]:  
	- zero add **kwargs into init  

0.3.11 (2024/06/04 09:39:47)
------------------------------
- [serialClient]:  
	- add write_read__last_validate_regexp  

0.3.10 (2024/06/03 17:40:10)
------------------------------
- [serialClient]:  
	- fix detects over base class!  

0.3.9 (2024/06/03 16:11:56)
------------------------------
- [serialClient]:  
	- extend write_read__last_validate for compare with list variants  

0.3.8 (2024/06/03 14:26:08)
------------------------------
- [serialClient]:  
	- add derivatives into INIT  

0.3.7 (2024/06/03 12:53:46)
------------------------------
- [serialClient]:  
	- add ADDRESSES__SYSTEM_FREE  
	- apply dict in ADDRESSES__SYSTEM  
	- add addresses__release/address__release  
	- rename buffers_clear*  
	- apply ADDRESS as property! and setter with address_release  
	- separate derivatives SerialClient_FirstFree/*  

0.3.6 (2024/05/31 15:27:27)
------------------------------
- [serialClient]:  
	- ensure keep all found ports in base class  

0.3.5 (2024/05/31 14:59:33)
------------------------------
- [values.py] move into funcs_aux!  
- [serialClient]:  
	- add _clear_buffer__write/clear_buffers/write_eol  
	- add+finish tests for client data processing  

0.3.4 (2024/05/29 17:44:03)
------------------------------
- [SerServer]fix logger  

0.3.3 (2024/05/29 14:53:12)
------------------------------
- [serialClient]:  
	- add address_check__resolved  
	- wr renames  
	- add write_read__last_validate  

0.3.2 (2024/05/29 12:16:20)
------------------------------
- [serialClient] fix connect  

0.3.1 (2024/05/29 11:57:53)
------------------------------
- [serialClient] fix address_get__first_free__paired as only for first address!  
- [serialServer] fix connect  

0.3.0 (2024/05/27 17:27:59)
------------------------------
- [serialClient] BIG REF:  
	- separate tests  
	- separate values+tests  
	- separate lineParsed+tests  
	- add address_paired__get  
	- rename all autodetect to address_get__first_free/*  
	- NEED FINISH FOR ALL!!!  

0.2.23 (2024/05/22 11:33:00)
------------------------------
- [__INIT__.py] fix import  
- apply last pypi template  

0.2.22 (2024/04/23 16:21:02)
------------------------------
- [linux] fix names returned from detect_system  

0.2.21 (2024/03/26 11:36:52)
------------------------------
- just zero increase version  

0.2.20 (2024/03/26 11:30:27)
------------------------------
- [SerialServer]:  
	- try add cmd__exit - and finally delete  
	- create cmd__script instead of cmd__run!!!  

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
- [SerialClient] place all important lists ADDRESSES__SYSTEM/PAIRED into base class(SerialClient)! so you can use Type__AddressAutoAcceptVariant.FIRST_PAIRED_0/1 in server!!!  

0.2.0 (2024/03/14 14:46:27)
------------------------------
- [SerialClient] BIG REF:  
	- ref address as TYPE__ADDRESS with autoconnect  
	- add lists ADDRESSES__SYSTEM/PAIRED  
	- [Type__AddressAutoAcceptVariant] add FIRST_SHORTED + FIRST_PAIRED_0/1  

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
- [SerialClient] separate Type__AddressAutoAcceptVariant inn class +add AUTODETECT by func  

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
