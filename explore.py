# DON'T DELETE!
# useful to start smth without pytest and not to run in main script!

from bus_user import *
import time


class DevEmulator(DevEmulator_CmdTheme):
    ADDRESS_APPLY_FIRST_VACANT = True
    TIMEOUT_READ = 2


emu = DevEmulator()
emu.start()

victim = BusSerial_Base()
victim.ADDRESS_APPLY_FIRST_VACANT = True
victim.connect()
victim.send__HELL(123)

emu.wait()
