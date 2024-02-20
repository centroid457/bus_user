# DON'T DELETE!
# useful to start smth without pytest and not to run in main script!

from bus_user import *


class DevEmulator(DevEmulator_CmdTheme):
    ADDRESS_APPLY_FIRST_VACANT = True
    TIMEOUT_READ = 3

emu = DevEmulator()
emu.start()
emu.wait()
