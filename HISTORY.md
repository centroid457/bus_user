# RELEASE HISTORY

********************************************************************************
## TODO
1. add all other port settings into SerialClient  
2. test work with several lines EOL__SEND  
3. TESTS with several PORTS!  

********************************************************************************
## FIXME
1. ...  

********************************************************************************
## NEWS

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
- [SerialClient] separate AddressAutoAcceptanceVariant inn class +add AUTODETECT by func  

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
