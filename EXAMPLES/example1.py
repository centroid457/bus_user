# NOTICE:
# 1. If bus cmd return several lines (DUMP for example) - you will get all of them in list! 
# 2. All answers you will get as string and you must parse it by youself!  
# errors will be get within it.


from bus_user import *

# SHOW (optional) COMMANDS EXPLICITLY by annotations without values!
# ------------------------------------------------------------------
class MySerialDevice(BusSerialBase__Getattr):
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

