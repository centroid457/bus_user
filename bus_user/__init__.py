from .history import *
from .bus_serial import *

# from .bus_i2c import *  # import only Linux supported modul return exx
try:
    from .bus_i2c import *    # import only Linux supported modul return exx
except:
    pass
