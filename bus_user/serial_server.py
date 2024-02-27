from .serial_client import SerialClient

from typing import *
import time
from object_info import ObjectInfo
from PyQt5.QtCore import QThread


# =====================================================================================================================
TYPE__CMD_RESULT = Union[str, List[str]]


# =====================================================================================================================
class AnswerVariants:
    SUCCESS: str = "OK"
    FAIL: str = "FAIL"
    UNSUPPORTED: str = "UNSUPPORTED"

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
    # REAL STATE --------------
    LINE: str       # ORIGINAL LINE!
    PREFIX: str
    CMD: str
    ARGS: List[str]
    KWARGS: Dict[str, str]      # not used by now

    # AUX ---------------------
    _PREFIX_EXPECTED: str

    def __init__(self, line: str, _prefix_expected: Optional[str] = None):
        line = str(line)

        # INIT ----------------
        self.LINE = line
        self.PREFIX = ""
        self.CMD = ""
        self.ARGS = []
        self.KWARGS = {}

        line_lower = line.lower()

        # PREFIX ----------------
        _prefix_expected = _prefix_expected or ""
        _prefix_expected = _prefix_expected.lower()
        self._PREFIX_EXPECTED = _prefix_expected
        if _prefix_expected and line_lower.startswith(_prefix_expected):
            self.PREFIX = _prefix_expected
            line_lower = line_lower.replace(_prefix_expected, "", 1)

        # BLANK ----------------------
        if not line_lower:
            return
        line_parts = line_lower.split()
        if not line_parts:
            return

        # CMD ------------------------
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

    def KWARGS_count(self) -> int:
        return len(self.KWARGS)


# =====================================================================================================================
class SerialServer_Base(QThread):
    # SETTINGS ------------------------------------------------
    SERIAL_CLIENT__CLS: Type[SerialClient] = SerialClient

    ADDRESS_APPLY_FIRST_VACANT: Optional[bool] = None
    ADDRESS: str = None

    ANSWER: Type[AnswerVariants] = AnswerVariants

    HELLO_MSG: List[str] = [
        "SerialServer_Base HELLO LINE 1",
        "SerialServer_Base hello line 2",
    ]

    PARAMS: Dict[str, Union[Any, Dict[Any, Any]]] = None

    # AUX -----------------------------------------------------
    _SERIAL_CLIENT: SerialClient

    _GETATTR_STARTSWITH__CMD: str = "cmd__"
    _GETATTR_STARTSWITH__SCRIPT: str = "script__"

    _NAMES__CMD: List[str]
    _NAMES__SCRIPT: List[str]

    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        # FIXME: deprecate param params??? used for tests
        super().__init__()

        self.PARAMS = params or self.PARAMS or {}
        self._names__init_lists()

        self._SERIAL_CLIENT = self.SERIAL_CLIENT__CLS()
        self._SERIAL_CLIENT.RAISE_READ_FAIL_PATTERN = False
        self._SERIAL_CLIENT._TIMEOUT__READ_FIRST = None
        # self._SERIAL_CLIENT._TIMEOUT__READ_LAST = None
        if self.ADDRESS is not None:
            self._SERIAL_CLIENT.ADDRESS = self.ADDRESS
        if self.ADDRESS_APPLY_FIRST_VACANT is not None:
            self._SERIAL_CLIENT.ADDRESS_APPLY_FIRST_VACANT = self.ADDRESS_APPLY_FIRST_VACANT

    def _names__init_lists(self) -> None:
        self._NAMES__CMD = []
        self._NAMES__SCRIPT = []

        for name in dir(self):
            name = name.lower()
            if name.startswith(self._GETATTR_STARTSWITH__CMD):
                self._NAMES__CMD.append(name.replace(self._GETATTR_STARTSWITH__CMD, "", 1))
            if name.startswith(self._GETATTR_STARTSWITH__SCRIPT):
                self._NAMES__SCRIPT.append(name.replace(self._GETATTR_STARTSWITH__SCRIPT, "", 1))

    # -----------------------------------------------------------------------------------------------------------------
    def run(self) -> None:
        if not self._SERIAL_CLIENT.connect():
            msg = f"[ERROR]NOT STARTED={self.__class__.__name__}"
            print(msg)
            return

        # self._SERIAL_CLIENT._write_line("")     # send blank=NO NEED!!!
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
        line_parsed = LineParsed(line, _prefix_expected=self._SERIAL_CLIENT.CMD_PREFIX)
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

        if line_parsed.CMD not in self._NAMES__CMD:
            return self._cmd__param_as_cmd(line_parsed)

        meth_cmd = getattr(self, f"{self._GETATTR_STARTSWITH__CMD}{line_parsed.CMD}")
        return meth_cmd(line_parsed)

    def _cmd__param_as_cmd(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        if not line_parsed.CMD:
            return ""

        if line_parsed.CMD not in self.PARAMS:
            return self.ANSWER.ERR__NAME_CMD_OR_PARAM

        return self.PARAMS[line_parsed.CMD]

    # -----------------------------------------------------------------------------------------------------------------
    def cmd__help(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        pass

        # WORK --------------------------------
        params_dump = []
        for name, value in self.PARAMS.items():
            if isinstance(value, dict):
                params_dump.append(f"{name}={{")
                for name_, value_ in value.items():
                    params_dump.append(f"    |{name_}={value_}")
            else:
                params_dump.append(f"{name}={value}")

        # WORK --------------------------------
        result = [
            *self.HELLO_MSG,
            "[PARAMS]:",
            *params_dump,
            "[CMDS]:",
            *[name for name in self._NAMES__CMD],
            "[SCRIPTS]:",
            *[name for name in self._NAMES__SCRIPT],
        ]
        return result

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
        if param_name not in self.PARAMS:
            return self.ANSWER.ERR__NAME_PARAM

        return self.PARAMS.get(param_name) or ""

    def cmd__set(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        if line_parsed.ARGS_count() != 2:
            return self.ANSWER.ERR__ARGS_VALIDATION

        # WORK --------------------------------
        param_name = line_parsed.ARGS[0]
        param_value = line_parsed.ARGS[1]
        if param_name not in self.PARAMS:
            return self.ANSWER.ERR__NAME_PARAM

        self.PARAMS[param_name] = param_value
        return self.ANSWER.SUCCESS

    def cmd__run(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        if line_parsed.ARGS_count() < 1:
            return self.ANSWER.ERR__ARGS_VALIDATION

        # WORK --------------------------------
        script_name = line_parsed.ARGS[0]
        if script_name not in self._NAMES__SCRIPT:
            return self.ANSWER.ERR__NAME_SCRIPT

        meth_scr = getattr(self, f"{self._GETATTR_STARTSWITH__SCRIPT}{script_name}")
        return meth_scr(line_parsed)


# =====================================================================================================================
class SerialServer_Base_Example(SerialServer_Base):
    PARAMS = {
        "NAME": "ATC",
        "ADDR": "01",
        # "NAME_ADDR": "01",  use as CMD!!!

    }

    def cmd__on(self) -> TYPE__CMD_RESULT:
        # do smth
        return self.ANSWER.SUCCESS

    def cmd__off(self) -> TYPE__CMD_RESULT:
        # do smth
        return self.ANSWER.SUCCESS

    def cmd__rst(self) -> TYPE__CMD_RESULT:
        # do smth
        return self.ANSWER.SUCCESS

    # -----------------------------------------------------------------------------------------------------------------
    def script__script1(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # do smth
        return self.ANSWER.SUCCESS


# =====================================================================================================================
