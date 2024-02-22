# DON'T DELETE!
# useful to start smth without pytest and not to run in main script!

from bus_user import *
import time
from object_info import ObjectInfo


class DevEmulator(SerialServer):
    ADDRESS_APPLY_FIRST_VACANT = True
    # TIMEOUT_READ = 2

emu = DevEmulator()
emu.start()


# victim = SerialClient()
# victim.ADDRESS_APPLY_FIRST_VACANT = True
# victim.connect()
#
# # ObjectInfo(victim._source).print()
# # exit()
#
# victim.send__HELL(123)
# victim.disconnect()

emu.wait()
