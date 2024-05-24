# =====================================================================================================================
# VERSION = (0, 0, 1)   # use import EXACT_OBJECTS! not *
#   from .main import *                 # INcorrect
#   from .main import EXACT_OBJECTS     # CORRECT


# =====================================================================================================================
# TEMPLATE
# from .main import (
#     # BASE
#     EXACT_OBJECTS,
#
#     # AUX
#
#     # TYPES
#
#     # EXX
# )
# ---------------------------------------------------------------------------------------------------------------------
from .history import HistoryIO
from .serial_client import (
    # BASE
    SerialClient,

    # AUX

    # TYPES
    TYPE__ADDRESS,
    TYPE__RW_ANSWER,

    Type__WrReturn,
    Type__AddressAutoAcceptVariant,

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
    Exx_SerialRead_FailDecoding,
    Exx_SerialPL2303IncorrectDriver,
)
from .serial_server import (
    # BASE
    SerialServer_Base,
    SerialServer_Echo,
    SerialServer_Example,

    # AUX
    Value_NotPassed,
    Value_WithUnit,
    Value_FromVariants,

    AnswerVariants,
    LineParsed,

    # TYPES
    TYPE__CMD_RESULT,

    # EXX
    Exx__ValueNotInVariants,
    Exx__VariantsIncompatible,
)
from .serial_derivatives import (
    # BASE
    SerialClient_Shorted,
    SerialClient_Emulated

    # AUX

    # TYPES

    # EXX
)

# from .bus_i2c import *  # import only Linux supported modul return exx
try:
    from .i2c_client import *    # import only Linux supported modul return exx
except:
    pass


# =====================================================================================================================
