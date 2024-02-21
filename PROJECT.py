from typing import *
from _aux__release_files import release_files_update


# =====================================================================================================================
VERSION = (0, 0, 3)   # 1/deprecate _VERSION_TEMPLATE from PRJ object +2/place update_prj here in __main__ +3/separate finalize attrs


# =====================================================================================================================
class PROJECT:
    # AUTHOR -----------------------------------------------
    AUTHOR_NAME: str = "Andrei Starichenko"
    AUTHOR_EMAIL: str = "centroid@mail.ru"
    AUTHOR_HOMEPAGE: str = "https://github.com/centroid457/"

    # PROJECT ----------------------------------------------
    NAME_IMPORT: str = "bus_user"
    KEYWORDS: List[str] = [
        "serial bus", "pyserial", "serial port", "com port", "comport", "rs232",
    ]
    CLASSIFIERS_TOPICS_ADD: List[str] = [
        # "Topic :: Communications",
        # "Topic :: Communications :: Email",
    ]

    # README -----------------------------------------------
    # add DOUBLE SPACE at the end of all lines! for correct representation in MD-viewers
    DESCRIPTION_SHORT: str = "work with equipment over buses like Serial/i2c/..."
    DESCRIPTION_LONG: str = """
    ### !. MOST APPROPRIATE COMMAND PROTOCOL
other protocols mot recommended

1. all cmds must be as params (preferred) in equipment or as special command
2. [<CMD_NAME>] - read param value or run special command  
    [IDN] - read value IDN  
    [DUMP] - run special command 
3. [<CMD_NAME> <VALUE>] - write value in parameter or run special cmd with param  
    [VOUT 12.3] - set value into parameter VOUT  
4. [<CMD_NAME> ?] - get available values to write into parameter  
    [MODE ?] - return [0 1 2 3]
5. all command sent must return answer  
    [OK] - if no value was asked
    [<VALUE>] - if asked some value, returned without measurement unit
    [FAIL] - any common not specified error
    [FAIL 0123] - any specified error without description
    [FAIL 02 VALUE OUT OF RANGE] - any specified error with description (full variant)
"""
    FEATURES: List[str] = [
        # "feat1",
        # ["feat2", "block1", "block2"],

        "Serial bus usage! with simply using commands",
        "connect with ADDRESS_APPLY_FIRST_VACANT",
    ]

    # HISTORY -----------------------------------------------
    VERSION: Tuple[int, int, int] = (0, 0, 5)
    TODO: List[str] = [
        "add all other port settings into BusSerial_Base",
        "test work with several lines EOL__SEND"
    ]
    FIXME: List[str] = [
        "..."
    ]
    NEWS: List[str] = [
        "connect with ADDRESS_APPLY_FIRST_VACANT",
        "_read_line char by char!!! with universal timeout"
    ]

    # FINALIZE -----------------------------------------------
    VERSION_STR: str = ".".join(map(str, VERSION))
    NAME_INSTALL: str = NAME_IMPORT.replace("_", "-")


# =====================================================================================================================
if __name__ == '__main__':
    release_files_update(PROJECT)


# =====================================================================================================================
