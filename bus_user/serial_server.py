from .serial_client import SerialClient

from typing import *
import time
import re
from object_info import ObjectInfo
from PyQt5.QtCore import QThread


import funcs_aux


# =====================================================================================================================
TYPE__CMD_RESULT = Union[str, List[str]]


# =====================================================================================================================
class AnswerVariants:
    SUCCESS: str = "OK"
    FAIL: str = "FAIL"
    UNSUPPORTED: str = "UNSUPPORTED"

    ERR__NAME_CMD_OR_PARAM: str = "ERR__NAME_CMD_OR_PARAM"
    ERR__NAME_SCRIPT: str = "ERR__NAME_SCRIPT"
    ERR__VALUE: str = "ERR__VALUE"
    ERR__ARGS_VALIDATION: str = "ERR__ARGS_VALIDATION"

    ERR__ENCODING_OR_DEVICE: str = "ERR__ENCODING_OR_DEVICE"
    ERR__SYNTAX: str = "ERR__SYNTAX"
    ERR__PARAM_CALLING: str = "ERR__PARAM_CALLING"


class LineParsed:
    """
    ALL RESULTS IN LOWERCASE! (EXCEPT ORIGINAL LINE!)
    """
    # REAL STATE --------------
    LINE: str       # ORIGINAL LINE!
    PREFIX: str
    CMD: str
    ARGS: List[str]
    KWARGS: Dict[str, str]

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
        line_lower = re.sub(r"\s*=+\s*", "=", line_lower)
        line_parts = line_lower.split()
        if not line_parts:
            return

        # ARGS/KWARGS ----------------
        for part in line_parts:
            if "=" not in part:
                self.ARGS.append(part)
            else:
                part__key_value = part.split("=")
                self.KWARGS.update(dict([part__key_value, ]))

        # CMD ------------------------
        if self.ARGS:
            self.CMD = self.ARGS[0]
            self.ARGS = self.ARGS[1:]

    def ARGS_count(self) -> int:
        return len(self.ARGS)

    def KWARGS_count(self) -> int:
        return len(self.KWARGS)


# =====================================================================================================================
class SerialServer_Base(QThread):
    # TODO: not realized - ACCESS RULES for PARAMS - may be not need in this case of class/situation!!!
    # TODO: not realised list access - best way to use pattern "name/index" and change same access with Dict "name/key"

    # SETTINGS ------------------------------------------------
    SERIAL_CLIENT__CLS: Type[SerialClient] = SerialClient

    ADDRESS_APPLY_FIRST_VACANT: Optional[bool] = None
    ADDRESS: str = None

    HELLO_MSG: List[str] = [
        "SerialServer_Base HELLO LINE 1",
        "SerialServer_Base hello line 2",
    ]

    PARAMS: Dict[str, Union[Any, Dict[Union[str, int], Any]]]
    ANSWER: Type[AnswerVariants] = AnswerVariants

    # AUX -----------------------------------------------------
    _SERIAL_CLIENT: SerialClient

    _GETATTR_STARTSWITH__CMD: str = "cmd__"
    _GETATTR_STARTSWITH__SCRIPT: str = "script__"

    _LIST__CMDS: List[str]
    _LIST__SCRIPTS: List[str]

    @property
    def _LIST__HELP(self) -> List[str]:
        params_dump = []
        for name, value in self.PARAMS.items():
            if isinstance(value, dict):
                params_dump.append(f"  |{name}={{")
                for name_, value_ in value.items():
                    params_dump.append(f"    |{name_}={value_}")
            else:
                params_dump.append(f"  |{name}={value}")

        # WORK --------------------------------
        result = [
            "-"*50,
            *self.HELLO_MSG,
            "[PARAMS]:",
            *params_dump,
            "[CMDS]:",
            *[f"  |{name}" for name in self._LIST__CMDS],
            "[SCRIPTS]:",
            *[f"  |{name}" for name in self._LIST__SCRIPTS],
            "[ANSWER_VARIANTS]:",
            *[f"  |{name}" for name in dir(self.ANSWER) if not name.startswith("__")],
            "-" * 50,
        ]
        return result

    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        # FIXME: deprecate param params??? used for tests
        super().__init__()

        self.PARAMS = params or self.PARAMS or {}
        self._init_lists()

        self._SERIAL_CLIENT = self.SERIAL_CLIENT__CLS()
        self._SERIAL_CLIENT.RAISE_READ_FAIL_PATTERN = False
        self._SERIAL_CLIENT._TIMEOUT__READ_FIRST = None
        if self.ADDRESS is not None:
            self._SERIAL_CLIENT.ADDRESS = self.ADDRESS
        if self.ADDRESS_APPLY_FIRST_VACANT is not None:
            self._SERIAL_CLIENT.ADDRESS_APPLY_FIRST_VACANT = self.ADDRESS_APPLY_FIRST_VACANT

    def _init_lists(self) -> None:
        self._LIST__CMDS = []
        self._LIST__SCRIPTS = []

        for name in dir(self):
            name = name.lower()
            if name.startswith(self._GETATTR_STARTSWITH__CMD):
                self._LIST__CMDS.append(name.replace(self._GETATTR_STARTSWITH__CMD, "", 1))
            if name.startswith(self._GETATTR_STARTSWITH__SCRIPT):
                self._LIST__SCRIPTS.append(name.replace(self._GETATTR_STARTSWITH__SCRIPT, "", 1))

    # -----------------------------------------------------------------------------------------------------------------
    def run(self) -> None:
        if not self._SERIAL_CLIENT.connect():
            msg = f"[ERROR]NOT STARTED={self.__class__.__name__}"
            print(msg)
            return

        self._SERIAL_CLIENT._write_line("")
        self._SERIAL_CLIENT._write_line("="*50)
        self._execute_line("hello")

        while True:
            line = None
            try:
                line = self._SERIAL_CLIENT.read_line()
            except:
                self._SERIAL_CLIENT._write_line(self.ANSWER.ERR__ENCODING_OR_DEVICE)

            if line:
                self._execute_line(line)

    def disconnect(self):
        self._SERIAL_CLIENT.disconnect()
        self.terminate()

    # -----------------------------------------------------------------------------------------------------------------
    def _execute_line(self, line: str) -> bool:
        line_parsed = LineParsed(line, _prefix_expected=self._SERIAL_CLIENT.CMD_PREFIX)
        cmd_result = self._cmd__(line_parsed)

        # blank line - SEND!!! because value may be BLANK!!!!
        # if not cmd_result:
        #     return True

        write_result = self._SERIAL_CLIENT._write_line(cmd_result)
        return write_result

    # CMD - ENTRY POINT -----------------------------------------------------------------------------------------------
    def _cmd__(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        meth_name__expected = f"{self._GETATTR_STARTSWITH__CMD}{line_parsed.CMD}"
        meth_name__original = funcs_aux.Iterables().item__get_original__case_insensitive(meth_name__expected, dir(self))
        if meth_name__original:
            meth_cmd = getattr(self, meth_name__original.VALUE)
        else:
            meth_cmd = self._cmd__param_as_cmd

        return meth_cmd(line_parsed)

    def _cmd__param_as_cmd(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # PREPARE -------------------------------
        if line_parsed.CMD:
            line_parsed.ARGS = [line_parsed.CMD, *line_parsed.ARGS]
            line_parsed.CMD = ""

        # VALIDATE -------------------------------
        if line_parsed.ARGS and line_parsed.KWARGS:
            return self.ANSWER.ERR__ARGS_VALIDATION

        # GET -------------------------------
        if line_parsed.ARGS:
            return self.cmd__get(line_parsed)

        # SET -----------------------------------
        if line_parsed.KWARGS:
            return self.cmd__set(line_parsed)

    # CMD - PARAMS ----------------------------------------------------------------------------------------------------
    def cmd__get(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        """
        use only single name!!!
        """
        # ERR__ARGS_VALIDATION --------------------------------
        pass

        # PREPARE --------------------------------
        ARGS = []
        for arg in line_parsed.ARGS:
            ARGS.extend(arg.split("/"))

        # WORK --------------------------------
        param_value = funcs_aux.Iterables().value_by_path__get(ARGS, self.PARAMS)
        if not param_value:
            return self.ANSWER.ERR__NAME_CMD_OR_PARAM

        param_value = param_value.VALUE

        # CALLABLE -------------------------------
        if callable(param_value):
            try:
                param_value = param_value()
            except:
                return self.ANSWER.ERR__PARAM_CALLING

        # NOTE - DONT return direct value! only str! cause of LIST would be assumed as list of lines! not the single line as single value!!!
        param_value = str(param_value)
        return param_value

    def cmd__set(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        """
        for ARGS - available only one param!
        for KWARGS - available MULTY params! fail protected!
        """
        # ERR__ARGS_VALIDATION -----------------
        if line_parsed.ARGS and line_parsed.KWARGS:
            return self.ANSWER.ERR__ARGS_VALIDATION
        if line_parsed.ARGS and line_parsed.ARGS_count() != 2:
            return self.ANSWER.ERR__ARGS_VALIDATION

        # PREPARE --------------------------------
        KWARGS = {**line_parsed.KWARGS}
        if line_parsed.ARGS:
            KWARGS = {line_parsed.ARGS[0]: line_parsed.ARGS[1]}

        # check exists all --------------
        for path_name in KWARGS:
            path_name__original = funcs_aux.Iterables().path__get_original(path_name, self.PARAMS)
            if not path_name__original:
                return self.ANSWER.ERR__NAME_CMD_OR_PARAM

        # SET --------------
        for path_name, path_value in KWARGS.items():
            path_value = funcs_aux.Strings().try_convert_to__elementary(path_value)
            result = funcs_aux.Iterables().value_by_path__set(path_name, path_value, self.PARAMS)

            if not result:
                return self.ANSWER.FAIL

        return self.ANSWER.SUCCESS

    # CMDS - STD ------------------------------------------------------------------------------------------------------
    def cmd__hello(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        pass

        # WORK --------------------------------
        return self.HELLO_MSG

    def cmd__help(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        pass

        # WORK --------------------------------
        return self._LIST__HELP

    def cmd__echo(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        pass

        # WORK --------------------------------
        return line_parsed.LINE

    # CMDS - SCRIPTS --------------------------------------------------------------------------------------------------
    def cmd__run(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        if line_parsed.ARGS_count() == 0:
            return self.ANSWER.ERR__ARGS_VALIDATION

        # WORK --------------------------------
        meth_name__expected = f"{self._GETATTR_STARTSWITH__SCRIPT}{line_parsed.ARGS[0]}"
        meth_name__original = funcs_aux.Iterables().item__get_original__case_insensitive(meth_name__expected, dir(self))
        if not meth_name__original:
            return self.ANSWER.ERR__NAME_SCRIPT

        meth_cmd = getattr(self, meth_name__original.VALUE)
        return meth_cmd(line_parsed)


# =====================================================================================================================
class SerialServer_Example(SerialServer_Base):
    PARAMS = {
        "VAR": "",

        "STR": "str",
        "STR_QUOTES": "str'",

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
    }

    def cmd__on(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # do smth
        return self.ANSWER.SUCCESS

    # -----------------------------------------------------------------------------------------------------------------
    def script__script1(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # do smth
        return self.ANSWER.SUCCESS


# =====================================================================================================================
