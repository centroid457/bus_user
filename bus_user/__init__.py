# =====================================================================================================================
# VERSION = (0, 0, 1)   # use import EXACT_OBJECTS! not *
#   from .main import *                 # INcorrect
#   from .main import EXACT_OBJECTS     # CORRECT


# =====================================================================================================================
from .history import HistoryIO
from .serial_client import (
    # BASE
    SerialClient,

    # AUX
    TYPE__RW_ANSWER, TYPE__ADDRESS,
    TypeWrReturn, AddressAutoAcceptVariant,

    # EXX
    Exx_SerialAddress_NotConfigured,
    Exx_SerialAddress_NotExists,
    Exx_SerialAddresses_NoVacant,
    Exx_SerialAddresses_NoAutodetected,
    Exx_SerialAddress_AlreadyOpened,
    Exx_SerialAddress_AlreadyOpened_InOtherObject,
    Exx_SerialAddress_OtherError,
    Exx_SerialRead_NotFullLine,
    Exx_SerialRead_FailPattern,
    Exx_SerialPL2303IncorrectDriver,
)
from .serial_server import (
    # BASE
    SerialServer_Base,
    SerialServer_Echo,
    SerialServer_Example,

    # AUX
    Value_NotPassed, Value_WithUnit, Value_FromVariants,
    TYPE__CMD_RESULT,
    AnswerVariants, LineParsed,

    # EXX
    Exx__ValueNotInVariants,
    Exx__VariantsIncompatible,
)
from .serial_derivatives import (
    # BASE
    SerialClient_Shorted, SerialClient_Emulated

    # AUX

    # EXX
)

# from .bus_i2c import *  # import only Linux supported modul return exx
try:
    from .i2c_client import *    # import only Linux supported modul return exx
except:
    pass


# =====================================================================================================================
