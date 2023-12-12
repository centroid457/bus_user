# bus_user
Designed to work with equipment over buses like Serial/i2c/...


## Features
1. Serial bus usage! with simply using commands


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

## GUIDE
### !. MOST APPROPRIATE COMMAND PROTOCOL
other protocols mot recommended

1. all cmds must be as params (preferred) in equipment or as special command
2. [<CMD_NAME>] - read param value or run special command  
    [IDN] - read value IDN  
    [DUMP] - run special command 
3. [<CMD_NAME> <VALUE>] - write value in parameter or run special cmd with param  
    [VOUT 12.3] - set value into parameter VOUT  


### 1. USAGE COMMANDS MAP
NOTICE: if bus cmd return several lines (DUMP for example) - you will get all of then in list! 


```python
from bus_user import *

# SHOW (optional) COMMANDS EXPLICITLY by annotations without values!
# ------------------------------------------------------------------
class MySerialDevice(BusSerial):
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
