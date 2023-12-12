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
### 1. USAGE COMMANDS MAP

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
