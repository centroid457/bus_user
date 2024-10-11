from bus_user import *

from typing import *
import time
import re
import logging
import datetime

from object_info import ObjectInfo
from PyQt5.QtCore import QThread

from funcs_aux import *


# =====================================================================================================================
pass


# =====================================================================================================================
# FIXME: this is just an attempt to replace simple dict!!!
class CmdSchema:
    NAME: str
    SCHEMA: Any | Valid | ValueNotExist = ValueNotExist
    TIMEOUT: float = 0
    DEFAULT: Any | ValueNotExist = ValueNotExist

    __value: Any = ValueNotExist

    # todo: add init

    @property
    def value(self) -> Any:
        pass
        # if self.__value == ValueNotExist:
        #     result = self.

        # return result

    @value.setter
    def value(self, other) -> None:
        self.__value = other

    def __init__(self, name):
        pass

    def __str__(self) -> str:
        return self.output()

    def output(self, value: Any | ValueNotExist = ValueNotExist) -> str:
        if value == ValueNotExist:
            value = self.DEFAULT

        if self.SCHEMA == ValueNotExist:
            return str(value)
        else:
            result = ValidAux.get_result_or_exx(self.SCHEMA, args=value)
            return str(result)


class CmdsSchema:
    """
    CREATED SPECIALLY FOR
    ---------------------
    serialClient - to keep default timeouts
    serialServer - to replace simple dictSchema my full needs about schemas
    """
    # default cmds
    # CMD1: CmdSchema = CmdSchema("CMD1", )

    # todo: add getattr by anyRegister
    # todo: add iterate

    def __init__(self, *schemas: tuple | CmdSchema) -> None:
        self.update(*schemas)

    def update(self, *schemas: tuple | CmdSchema) -> None:
        """
        overwrite existed schemas!
        """
        for schema in schemas:
            if not isinstance(schema, CmdSchema):
                schema = CmdSchema(*schema)

            setattr(self, schema.NAME, schema)


# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
class SerialServer_Example(SerialServer_Base):
    PARAMS = {
        "VAR": "",

        "STR": "str",
        "QUOTE": "str'",

        "BLANC": "",
        "ZERO": 0,

        "NONE": None,
        "TRUE": True,
        "FALSE": False,

        "INT": 1,
        "FLOAT": 1.1,

        "CALL": time.time,
        "EXX": time.strftime,

        "LIST": [0, 1, 2],
        "LIST_2": [[11]],
        "_SET": {0, 1, 2},
        "DICT_SHORT": {1: 11},
        "DICT_SHORT_2": {"HEllo": {1: 11}},
        "DICT": {
            1: 111,
            "2": 222,
            3: {
                1: 31,
                2: 32,
            },
        },
        "UNIT": ValueUnit(1, unit="V"),
        "VARIANT": ValueVariants(220, variants=[220, 380]),
    }

    def cmd__upper(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # usefull for tests
        return line_parsed.ORIGINAL.upper()

    def cmd__lower(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        return line_parsed.ORIGINAL.lower()

    def cmd__cmd(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # NOTE: NONE is equivalent for SUCCESS
        # do smth
        pass

    def cmd__cmd_no_line(self) -> TYPE__CMD_RESULT:
        # NOTE: NONE is equivalent for SUCCESS
        # do smth
        pass

    # -----------------------------------------------------------------------------------------------------------------
    def script__script1(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # do smth
        pass


# =====================================================================================================================
if __name__ == "__main__":
    SerialServer_Example().run()


# =====================================================================================================================
