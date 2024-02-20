from .serial_user import BusSerial_Base, BusSerialBase__GetattrDictDirect

from typing import *
from object_info import ObjectInfo
from PyQt5.QtCore import QThread


# =====================================================================================================================
class AnswerResult:
    SUCCESS: str = "OK"
    ERR__NAME_CMD: str = "ERR__NAME_CMD"
    ERR__NAME_SCRIPT: str = "ERR__NAME_SCRIPT"
    ERR__NAME_PARAM: str = "ERR__NAME_PARAM"
    ERR__VALUE: str = "ERR__VALUE"
    ERR__ARGS_VALIDATION: str = "ERR__ARGS_VALIDATION"


class LineParsed:
    # PREFIX: str = ""
    CMD: str
    ARGS: List[str]
    KWARGS: Dict[str, str]

    def __init__(self, line: str, prefix: Optional[str] = None):
        self.CMD = ""
        self.ARGS = []
        self.KWARGS = {}

        prefix = prefix or ""
        if prefix and line.startswith(prefix):
            line = line.replace(prefix, "")

        line_parts = line.split()
        self.CMD = line_parts[0]

        if len(line_parts) == 1:
            return

        for part in line_parts[1:]:
            if "=" not in part:
                self.ARGS.append(part)
            else:
                part__key_value = part.split("=")
                self.KWARGS.update(dict([part__key_value, ]))


# =====================================================================================================================
class DevEmulator_Base:
    SERIAL_CLS: Type[BusSerial_Base] = BusSerialBase__GetattrDictDirect
    SERIAL: BusSerial_Base

    def __init__(self):
        super().__init__()
        self.SERIAL = self.SERIAL_CLS()


# =====================================================================================================================
class DevEmulator_DirectDict(DevEmulator_Base, QThread):
    pass


# =====================================================================================================================
class DevEmulator_CmdTheme(DevEmulator_Base, QThread):
    _PARAMS: Dict[str, Any]

    STARTSWITH__CMD: str = "cmd__"
    STARTSWITH__SCRIPT: str = "script__"

    def __init__(self, params: Dict[str, Any]):
        self._PARAMS = params
        super().__init__()

    def run(self) -> None:
        if not self.SERIAL.connect():
            msg = f"[ERROR]NOT STARTED={self.__class__.__name__}"
            print(msg)
            return
        while True:
            line = self.SERIAL._read_line(_timeout=0.5)
            if line:
                self.execute_line(line)

    # -----------------------------------------------------------------------------------------------------------------
    def execute_line(self, line: str) -> str:
        line_parsed = LineParsed(line, prefix=self.SERIAL.CMD_PREFIX)
        return self.cmd__(line_parsed)

    # -----------------------------------------------------------------------------------------------------------------
    def cmd__(self, line_parsed: LineParsed) -> str:
        meth_cmd = getattr(self, f"{self.STARTSWITH__CMD}{line_parsed.CMD}")
        if not meth_cmd:
            return AnswerResult.ERR__NAME_CMD

        return meth_cmd(line_parsed)

    def cmd__GET(self, line_parsed: LineParsed) -> str:
        # ERR__ARGS_VALIDATION --------------------------------
        if len(line_parsed.ARGS) != 1:
            return AnswerResult.ERR__ARGS_VALIDATION

        # WORK --------------------------------
        param_name = line_parsed.ARGS[0]
        if param_name not in self._PARAMS:
            return AnswerResult.ERR__NAME_PARAM

        return self._PARAMS.get(param_name) or ""

    def cmd__SET(self, line_parsed: LineParsed) -> str:
        # ERR__ARGS_VALIDATION --------------------------------
        if len(line_parsed.ARGS) != 2:
            return AnswerResult.ERR__ARGS_VALIDATION

        # WORK --------------------------------
        param_name = line_parsed.ARGS[0]
        param_value = line_parsed.ARGS[1]
        if param_name not in self._PARAMS:
            return AnswerResult.ERR__NAME_PARAM

        self._PARAMS[param_name] = param_value
        return AnswerResult.SUCCESS

    def cmd__RUN(self, line_parsed: LineParsed) -> str:
        # ERR__ARGS_VALIDATION --------------------------------
        if len(line_parsed.ARGS) < 1:
            return AnswerResult.ERR__ARGS_VALIDATION

        # WORK --------------------------------
        script_name = line_parsed.ARGS[0]
        meth_scr = getattr(self, f"{self.STARTSWITH__SCRIPT}{script_name}")
        if not meth_scr:
            return AnswerResult.ERR__NAME_SCRIPT

        return meth_scr()

    # -----------------------------------------------------------------------------------------------------------------
    def script__SCRIPT1(self, line_parsed: LineParsed) -> str:
        # do smth
        return AnswerResult.SUCCESS


# =====================================================================================================================
class DevEmulator_ATC(DevEmulator_CmdTheme):
    def cmd__ON(self) -> str:
        # do smth
        return AnswerResult.SUCCESS

    def cmd__OFF(self) -> str:
        # do smth
        return AnswerResult.SUCCESS

    def cmd__RST(self) -> str:
        # do smth
        return AnswerResult.SUCCESS


# =====================================================================================================================
