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
from .line_parser import LineParsed
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
    Exx_SerialAddress_NotApplyed,
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
    AnswerVariants,
    # TYPES
    TYPE__CMD_RESULT,
    # EXX
)
from .serial_derivatives import (
    # BASE
    SerialClient_FirstFree,
    SerialClient_FirstFree_Shorted,
    SerialClient_FirstFree_Paired,
    SerialClient_FirstFree_AnswerValid,
    SerialClient_Emulated,
    # AUX
    # TYPES
    # EXX
)

from requirements_checker import ReqCheckStr_Os
if ReqCheckStr_Os.bool_if__LINUX():
    from .i2c_client import (
        # BASE
        BusI2c,
        # AUX
        Patterns,
        # TYPES
        # EXX
        Exx_I2cConnection,
    )


# =====================================================================================================================
