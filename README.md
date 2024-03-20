# bus_user (v0.2.15)

## DESCRIPTION_SHORT
work with equipment over buses like Serial/i2c/... as client and server

## DESCRIPTION_LONG
### !. MOST APPROPRIATE COMMAND PROTOCOL
other protocols mot recommended

1. all cmds must be as params (preferred) in equipment or as special command
2. [<CMD_NAME>] - read param value or run special command  
    [IDN] - read value IDN  
    [DUMP] - run special command 
3. [<CMD_NAME> <VALUE>] - write value in parameter or run special cmd with param  
    [VOUT 12.3] - set value into parameter VOUT  
4. [<CMD_NAME> ?] - get available values to write into parameter  
    [MODE ?] - return [0 1 2 3]
5. all command sent must return answer  
    [OK] - if no value was asked
    [<VALUE>] - if asked some value, returned without measurement unit
    [FAIL] - any common not specified error
    [FAIL 0123] - any specified error without description
    [FAIL 02 VALUE OUT OF RANGE] - any specified error with description (full variant)


## Features
1. Serial:  
	- Client+Server  
	- connect with AddressAutoAcceptVariant FIRST_FREE/FIRST_FREE__ANSWER_VALID  
	- set/get params by SlashOrSpacePath addressing  
	- handle BackSpace send manually from terminal  
2. SerialServer values:  
	- as Callable  
	- Value_WithUnit  
	- Value_FromVariants  
	- list_results  
3. SerialServer cmd:  
	- NONE is equivalent for SUCCESS  
	- no need params (like line_parsed as before)  
	- help - for show all variants (Units/Variants/Callables)!  


********************************************************************************
## License
See the [LICENSE](LICENSE) file for license rights and limitations (MIT).


## Release history
See the [HISTORY.md](HISTORY.md) file for release history.


## Installation
```commandline
pip install bus-user
```


## Import
```python
from bus_user import *
```


********************************************************************************
## USAGE EXAMPLES
See tests and sourcecode for other examples.

------------------------------
### 1. example1.py
```python
# NOTICE:
# 1. If bus cmd return several lines (DUMP for example) - you will get all of them in list! 
# 2. All answers you will get as string and you must parse it by youself!  
# errors will be get within it.


from bus_user import *

# SHOW (optional) COMMANDS EXPLICITLY by annotations without values!
# ------------------------------------------------------------------
class MySerialDevice(SerialClient):
    IDN: Callable[[Any], TYPE__RW_ANSWER]
    ADDR: Callable[[Any], TYPE__RW_ANSWER]
    DUMP: Callable[[Any], TYPE__RW_ANSWER]

# USE in code
# -----------
dev = MySerialDevice()
if dev.connect():
    answer1 = dev.IDN()   # return answer for sent string in port "IDN"
    answer2 = dev.VIN()   # return answer for sent string in port "VIN"
    answer3 = dev.VIN(12)   # return answer for sent string in port "VIN 12"
    answer4 = dev.VIN("12")   # return answer for sent string in port "VIN 12"
```

********************************************************************************
