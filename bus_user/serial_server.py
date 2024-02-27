from .serial_client import SerialClient

from typing import *
import time
from object_info import ObjectInfo
from PyQt5.QtCore import QThread


# =====================================================================================================================
TYPE__CMD_RESULT = Union[str, List[str]]


# =====================================================================================================================
class AnswerKit:
    SUCCESS: str = "OK"
    ERR__NAME_CMD_OR_PARAM: str = "ERR__NAME_CMD_OR_PARAM"
    ERR__NAME_SCRIPT: str = "ERR__NAME_SCRIPT"
    ERR__NAME_PARAM: str = "ERR__NAME_PARAM"
    ERR__VALUE: str = "ERR__VALUE"
    ERR__ARGS_VALIDATION: str = "ERR__ARGS_VALIDATION"
    ERR__ENCODING_OR_DEVICE: str = "ERR__ENCODING_OR_DEVICE"


class LineParsed:
    """
    ALL RESULTS IN LOWERCASE! (EXCEPT ORIGINAL LINE!)
    """
    # PREFIX: str = ""
    LINE: str
    CMD: str
    ARGS: List[str]
    KWARGS: Dict[str, str]      # not used now

    def __init__(self, line: str, prefix: Optional[str] = None):
        # INIT ----------------
        self.LINE = line
        self.CMD = ""
        self.ARGS = []
        self.KWARGS = {}

        line = line.lower()
        # PREFIX ----------------
        if prefix:
            prefix.lower()
        prefix = prefix or ""
        if prefix and line.startswith(prefix):
            line = line.replace(prefix, "")

        # BLANK ----------------
        if not line:
            return
        line_parts = line.split()
        if not line_parts:
            return

        # CMD ----------------
        self.CMD = line_parts[0]

        # ARGS/KWARGS ----------------
        if len(line_parts) == 1:
            return
        for part in line_parts[1:]:
            if "=" not in part:
                self.ARGS.append(part)
            else:
                part__key_value = part.split("=")
                self.KWARGS.update(dict([part__key_value, ]))

    def ARGS_count(self) -> int:
        return len(self.ARGS)


# =====================================================================================================================
class SerialServer(QThread):
    # SETTINGS ------------------------------------------------
    SERIAL_USER_CLS: Type[SerialClient] = SerialClient

    ADDRESS_APPLY_FIRST_VACANT: Optional[bool] = None
    ADDRESS: str = None

    ANSWER: Type[AnswerKit] = AnswerKit

    HELLO_MSG: TYPE__CMD_RESULT = [
        "SerialServer HELLO LINE 1",
        "SerialServer hello line 2",
    ]

    # AUX -----------------------------------------------------
    _SERIAL_CLIENT: SerialClient

    _GETATTR_STARTSWITH__CMD: str = "cmd__"
    _GETATTR_STARTSWITH__SCRIPT: str = "script__"

    # INIT -----------------------------------------------------
    _PARAMS: Dict[str, Any]

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        super().__init__()

        self._PARAMS = params or {}

        self._SERIAL_CLIENT = self.SERIAL_USER_CLS()
        self._SERIAL_CLIENT.RAISE_READ_FAIL_PATTERN = False
        self._SERIAL_CLIENT._TIMEOUT__READ_FIRST = None
        # self._SERIAL_CLIENT._TIMEOUT__READ_LAST = None
        if self.ADDRESS is not None:
            self._SERIAL_CLIENT.ADDRESS = self.ADDRESS
        if self.ADDRESS_APPLY_FIRST_VACANT is not None:
            self._SERIAL_CLIENT.ADDRESS_APPLY_FIRST_VACANT = self.ADDRESS_APPLY_FIRST_VACANT
        self._SERIAL_CLIENT.connect()

    def run(self) -> None:
        if not self._SERIAL_CLIENT.connect():
            msg = f"[ERROR]NOT STARTED={self.__class__.__name__}"
            print(msg)
            return

        self._SERIAL_CLIENT._write_line("")     # send blank
        self.execute_line("hello")

        while True:
            line = None
            try:
                line = self._SERIAL_CLIENT.read_line()
            except:
                self._SERIAL_CLIENT._write_line(self.ANSWER.ERR__ENCODING_OR_DEVICE)

            if line:
                self.execute_line(line)

    def disconnect(self):
        self._SERIAL_CLIENT.disconnect()
        self.terminate()

    # -----------------------------------------------------------------------------------------------------------------
    def execute_line(self, line: str) -> bool:
        line_parsed = LineParsed(line, prefix=self._SERIAL_CLIENT.CMD_PREFIX)
        cmd_result = self._cmd__(line_parsed)

        # blank line
        if not cmd_result:
            return True

        write_result = self._SERIAL_CLIENT._write_line(cmd_result)
        return write_result

    # -----------------------------------------------------------------------------------------------------------------
    def _cmd__(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        if not line_parsed.CMD:
            return ""

        meth_cmd_name = f"{self._GETATTR_STARTSWITH__CMD}{line_parsed.CMD}"

        if not hasattr(self, meth_cmd_name):
            return self._cmd__param_as_cmd(line_parsed)

        meth_cmd = getattr(self, meth_cmd_name)
        return meth_cmd(line_parsed)

    def _cmd__param_as_cmd(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        if not line_parsed.CMD:
            return ""

        if line_parsed.CMD not in self._PARAMS:
            return self.ANSWER.ERR__NAME_CMD_OR_PARAM

        return self._PARAMS[line_parsed.CMD]

    # -----------------------------------------------------------------------------------------------------------------
    def cmd__hello(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        pass

        # WORK --------------------------------
        return self.HELLO_MSG

    def cmd__echo(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        pass

        # WORK --------------------------------
        return line_parsed.LINE

    def cmd__get(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        if line_parsed.ARGS_count() != 1:
            return self.ANSWER.ERR__ARGS_VALIDATION

        # WORK --------------------------------
        param_name = line_parsed.ARGS[0]
        if param_name not in self._PARAMS:
            return self.ANSWER.ERR__NAME_PARAM

        return self._PARAMS.get(param_name) or ""

    def cmd__set(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        if line_parsed.ARGS_count() != 2:
            return self.ANSWER.ERR__ARGS_VALIDATION

        # WORK --------------------------------
        param_name = line_parsed.ARGS[0]
        param_value = line_parsed.ARGS[1]
        if param_name not in self._PARAMS:
            return self.ANSWER.ERR__NAME_PARAM

        self._PARAMS[param_name] = param_value
        return self.ANSWER.SUCCESS

    def cmd__run(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        if line_parsed.ARGS_count() < 1:
            return self.ANSWER.ERR__ARGS_VALIDATION

        # WORK --------------------------------
        script_name = line_parsed.ARGS[0]
        meth_script_name = f"{self._GETATTR_STARTSWITH__SCRIPT}{script_name}"
        if not hasattr(self, meth_script_name):
            return self.ANSWER.ERR__NAME_SCRIPT

        meth_scr = getattr(self, meth_script_name)
        return meth_scr(line_parsed)

    # -----------------------------------------------------------------------------------------------------------------
    def script__script1(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # do smth
        return self.ANSWER.SUCCESS


# =====================================================================================================================
class SerialServer_ATC(SerialServer):
    def cmd__on(self) -> TYPE__CMD_RESULT:
        # do smth
        return self.ANSWER.SUCCESS

    def cmd__off(self) -> TYPE__CMD_RESULT:
        # do smth
        return self.ANSWER.SUCCESS

    def cmd__rst(self) -> TYPE__CMD_RESULT:
        # do smth
        return self.ANSWER.SUCCESS


# =====================================================================================================================
