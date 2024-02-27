# DON'T DELETE!
# useful to start smth without pytest and not to run in main script!

from bus_user import *
import time
from object_info import ObjectInfo


class DevEmulator(SerialServer_Base):
    ADDRESS_APPLY_FIRST_VACANT = True


emu = DevEmulator()
emu.start()


# victim = SerialClient()
# victim.ADDRESS_APPLY_FIRST_VACANT = True
# victim.connect()
#
# # ObjectInfo(victim._SERIAL).print()
# # exit()
#
# victim.send__HELL(123)
# victim.disconnect()

emu.wait()
