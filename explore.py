# DON'T DELETE!
# useful to start smth without pytest and not to run in main script!

from bus_user import *
import time
from object_info import ObjectInfo


class DevEmulator(SerialServer_Example):
    pass
    ADDRESS = AddressAutoAcceptVariant.FIRST_FREE   # FIXME: NOTE - be careful about connecting with shorted PORT! unplug it!


emu = DevEmulator()
emu.start()


# victim = SerialClient()
# victim.ADDRESS = AddressAutoAcceptVariant.FIRST_FREE
# victim.connect()
#
# # ObjectInfo(victim._SERIAL).print()
# # exit()
#
# victim.send__HELL(123)
# victim.disconnect()

emu.wait()
