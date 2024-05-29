from bus_user import *

from typing import *
import time
import re
import logging
import datetime

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
    ERR__VALUE_INCOMPATIBLE: str = "ERR__VALUE_INCOMPATIBLE"
    ERR__ARGS_VALIDATION: str = "ERR__ARGS_VALIDATION"

    ERR__ENCODING_OR_DEVICE: str = "ERR__ENCODING_OR_DEVICE"
    ERR__SYNTAX: str = "ERR__SYNTAX"
    ERR__PARAM_CALLING: str = "ERR__PARAM_CALLING"

    EXIT: str = "EXIT"


# =====================================================================================================================
class SerialServer_Base(QThread):
    # TODO: not realized - ACCESS RULES for PARAMS - may be not need in this case of class/situation!!!
    # TODO: not realised list access - best way to use pattern "name/index" and change same access with Dict "name/key"

    # SETTINGS ------------------------------------------------
    _SERIAL_CLIENT__CLS: Type[SerialClient] = SerialClient  # usually not redefines!
    SERIAL_CLIENT: SerialClient
    ADDRESS: str = None     # DON'T DEPRECATE! usually use only as exact port or keep NONE!

    HELLO_MSG__SEND_ON_START: bool = True   # don't set here on True! use it only as overwritten if needed!!!
    HELLO_MSG: List[str] = [
        "SerialServer_Base HELLO line 1",
        "SerialServer_Base hello line 2",
    ]

    PARAMS: Dict[str, Union[Any, Dict[Union[str, int], Any]]] = None
    ANSWER: Type[AnswerVariants] = AnswerVariants

    # AUX -----------------------------------------------------
    _STARTSWITH__CMD: str = "cmd__"
    _STARTSWITH__SCRIPT: str = "script__"

    _LIST__CMDS: List[str]
    _LIST__SCRIPTS: List[str]

    CYCLE_ACTIVE: bool = None  # active working state on ReadingWriting - used for waiting active state!

    def wait__cycle_active(self) -> None:
        """
        ALWAYS WAIT IT BEFORE START EXPLUATATION!
        """
        self.logger.debug("")

        while not self.CYCLE_ACTIVE:
            time.sleep(0.5)

    @property
    def _LIST__HELP(self) -> List[str]:
        params_dump = []
        for name, value in self.PARAMS.items():
            if isinstance(value, dict):
                params_dump.append(" "*2 + f"|{name}={{")
                for name_, value_ in value.items():
                    params_dump.append(" "*4 + f"|{name_}={value_}")
            elif isinstance(value, (Value_WithUnit, Value_FromVariants)):
                params_dump.append(" "*2 + f"|{name}={repr(value)}")
            else:
                params_dump.append(" "*2 + f"|{name}={value}")

        # WORK --------------------------------
        result = [
            "="*50,
            *self.HELLO_MSG,
            "-" * 50,
            "[PARAMS]:",
            *params_dump,
            "-" * 50,
            "[CMDS]:",
            *[f"  |{name}" for name in self._LIST__CMDS],
            "-" * 50,
            "[SCRIPTS]:",
            *[f"  |{name}" for name in self._LIST__SCRIPTS],
            "-" * 50,
            "[ANSWER_VARIANTS]:",
            *[f"  |{name}" for name in dir(self.ANSWER) if not name.startswith("__")],
            "=" * 50,
        ]
        return result

    def list_param_results(self, lines: List[str]) -> List[str]:
        """
        used to show several PARAMS and CMD results (ready to pretty sent in serial port)
        cmds used as params in just case if cmd returns exact value! (not for any cmd and not used for results as Answer)
        """
        result = []
        for line in lines:
            line_parsed = LineParsed(line, _prefix_expected=self.SERIAL_CLIENT.PREFIX)
            line_result = self._cmd__(line_parsed)
            result.append(f"{line}={line_result}")

        return result

    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, params: Dict[str, Any] = None):
        # FIXME: deprecate param params??? used for tests?
        super().__init__()

        self._init__logger()
        self.logger.debug('init SerialServer')

        if params:
            self.PARAMS = params
        elif not self.PARAMS:
            self.PARAMS = {}
        else:
            pass

        self._init__lists()

        self.SERIAL_CLIENT = self._SERIAL_CLIENT__CLS()
        self.SERIAL_CLIENT.RAISE_READ_FAIL_PATTERN = False
        self.SERIAL_CLIENT.TIMEOUT__READ = None
        if self.ADDRESS:
            self.SERIAL_CLIENT.ADDRESS = self.ADDRESS
        if not self.SERIAL_CLIENT.ADDRESS:
            self.SERIAL_CLIENT.ADDRESS = Type__AddressAutoAcceptVariant.FIRST_FREE__PAIRED   # here keep only FIRST_FREE__PAIRED! as default!

    def _init__lists(self) -> None:
        self._LIST__CMDS = []
        self._LIST__SCRIPTS = []

        for name in dir(self):
            name = name.lower()
            if name.startswith(self._STARTSWITH__CMD):
                self._LIST__CMDS.append(name.replace(self._STARTSWITH__CMD, "", 1))
            if name.startswith(self._STARTSWITH__SCRIPT):
                self._LIST__SCRIPTS.append(name.replace(self._STARTSWITH__SCRIPT, "", 1))

    def _init__logger(self) -> None:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        _formatter = logging.Formatter(
            '%(asctime)s[%(levelname)s/thread%(thread)s]%(name)s(%(filename)s).%(funcName)s(line%(lineno)d)%(msg)s')

        # _handler_file = logging.FileHandler(f"SerialServer_Base{datetime.datetime.now()}.log")
        _handler_file = logging.FileHandler(f"SerialServer_Base.log")
        _handler_file.setFormatter(_formatter)

        _handler_std = logging.StreamHandler()
        _handler_std.setFormatter(_formatter)

        logger.addHandler(_handler_file)
        logger.addHandler(_handler_std)

        logger.debug('LOGGER INITED')
        self.logger = logger

    # -----------------------------------------------------------------------------------------------------------------
    def run(self) -> None:
        self.logger.debug("")

        if self.CYCLE_ACTIVE:
            # just for sure
            msg = f"[WARN] ALREADY STARTED={self.__class__.__name__}"
            print(msg)
            return

        if not self.SERIAL_CLIENT.connect(_raise=False):
            msg = f"[ERROR]NOT STARTED={self.__class__.__name__}"
            print(msg)
            return

        if self.HELLO_MSG__SEND_ON_START:
            additional_line = f"Started on [{self.SERIAL_CLIENT._SERIAL.port}]"
            if additional_line not in self.HELLO_MSG:
                self.HELLO_MSG.append(additional_line)
            self.SERIAL_CLIENT._write_line("")
            self.SERIAL_CLIENT._write_line("="*50)
            # self._execute_line("hello")
            self.SERIAL_CLIENT._write_line(self.HELLO_MSG)

        self._cycle__activate()

    def _cycle__activate(self) -> Never:
        self.logger.debug("")

        while True:
            self.CYCLE_ACTIVE = True
            line = None
            try:
                line = self.SERIAL_CLIENT.read_line()
            except:
                self.SERIAL_CLIENT._write_line(self.ANSWER.ERR__ENCODING_OR_DEVICE)

            if line:
                self._execute_line(line)

    def connect(self) -> None:
        self.logger.debug("")
        self.start()

    def start(self, *args, **kwargs):
        if not self.isRunning():
            super().start()
            self.wait__cycle_active()

    def disconnect(self):
        self.logger.debug("")

        self.terminate()
        # self.SERIAL_CLIENT.disconnect()
        # self.CYCLE_ACTIVE = False

    def terminate(self):
        # if self.SERIAL_CLIENT.CONNECTED:
        #     self.SERIAL_CLIENT.send__(self.ANSWER.EXIT)

        self.SERIAL_CLIENT.disconnect()

        if self.isRunning():
            self.logger.debug("")
            super().terminate()
        self.CYCLE_ACTIVE = False

    # -----------------------------------------------------------------------------------------------------------------
    def _execute_line(self, line: str) -> bool:
        self.logger.debug("")

        line_parsed = LineParsed(line, _prefix_expected=self.SERIAL_CLIENT.PREFIX)
        cmd_result = self._cmd__(line_parsed)

        # blank line - SEND!!! because value may be BLANK!!!!
        # if not cmd_result:
        #     return True

        write_result = self.SERIAL_CLIENT._write_line(cmd_result)
        return write_result

    # CMD - ENTRY POINT -----------------------------------------------------------------------------------------------
    def _cmd__(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        self.logger.debug("")

        meth_name__expected = f"{self._STARTSWITH__CMD}{line_parsed.CMD}"
        meth_name__original = funcs_aux.Iterables().item__get_original__case_insensitive(meth_name__expected, dir(self))
        # GET METHOD --------------------
        if meth_name__original:
            meth = getattr(self, meth_name__original.VALUE)
        else:
            meth = self._cmd__param_as_cmd

        # EXEC METHOD --------------------
        try:
            result = meth(line_parsed)
        except TypeError as exx:
            try:
                result = meth()
            except:
                result = self.ANSWER.FAIL
        except:
            result = self.ANSWER.FAIL

        if result is None:
            result = self.ANSWER.SUCCESS
        return result

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

        # VARIANTS ------------------------------------------------------------------
        # Value_WithUnit -------------------------------
        if isinstance(param_value, (Value_FromVariants, Value_FromVariants)):
            return str(param_value)

        # CALLABLE -------------------------------
        # todo: add call func with remaining ARGS as func positional params??
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

        # VALIDATE = check AVAILABLE TO CHANGE = exists all and not callable --------------
        for path, value_new in KWARGS.items():
            path_name__original = funcs_aux.Iterables().path__get_original(path, self.PARAMS)
            if not path_name__original:
                return self.ANSWER.ERR__NAME_CMD_OR_PARAM

            value_old = funcs_aux.Iterables().value_by_path__get(path, self.PARAMS).VALUE
            if isinstance(value_old, Value_WithUnit):
                # NOTE: ALL CLASSES/INSTANCES ARE CALLABLE!!!
                pass
            elif isinstance(value_old, Value_FromVariants):
                if value_new not in value_old:
                    return self.ANSWER.ERR__VALUE_INCOMPATIBLE
            elif callable(value_old):
                return self.ANSWER.ERR__NAME_CMD_OR_PARAM

        # SET --------------
        for path, value_new in KWARGS.items():
            value_new = funcs_aux.Strings().try_convert_to__elementary(value_new)
            value_old = funcs_aux.Iterables().value_by_path__get(path, self.PARAMS).VALUE
            # SET ----------
            if isinstance(value_old, (Value_WithUnit, Value_FromVariants)):
                try:
                    value_old.value = value_new
                    result = True
                except:
                    return self.ANSWER.ERR__VALUE_INCOMPATIBLE
            else:
                result = funcs_aux.Iterables().value_by_path__set(path, value_new, self.PARAMS)

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
        return line_parsed.ORIGINAL

    # CMDS - SCRIPTS --------------------------------------------------------------------------------------------------
    def cmd__script(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        """
        it is as template! you can create/use your awn script-run cmd!
        """
        return self._script__(line_parsed)

    def _script__(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
        # ERR__ARGS_VALIDATION --------------------------------
        if line_parsed.ARGS_count() == 0:
            return self.ANSWER.ERR__ARGS_VALIDATION

        # WORK --------------------------------
        meth_name__expected = f"{self._STARTSWITH__SCRIPT}{line_parsed.ARGS[0]}"
        meth_name__original = funcs_aux.Iterables().item__get_original__case_insensitive(meth_name__expected, dir(self))
        if not meth_name__original:
            return self.ANSWER.ERR__NAME_SCRIPT

        meth = getattr(self, meth_name__original.VALUE)

        # EXEC METHOD --------------------
        try:
            result = meth(line_parsed)
        except TypeError as exx:
            try:
                result = meth()
            except:
                result = self.ANSWER.FAIL
        except:
            result = self.ANSWER.FAIL

        if result is None:
            result = self.ANSWER.SUCCESS
        return result

    # def cmd__exit(self, line_parsed: LineParsed) -> TYPE__CMD_RESULT:
    #     self.disconnect()
    #     exit()


# =====================================================================================================================
class SerialServer_Echo(SerialServer_Base):
    HELLO_MSG: List[str] = [
        "SerialServer_Echo",
    ]

    def _execute_line(self, line: str) -> bool:
        write_result = self.SERIAL_CLIENT._write_line(line)
        return write_result


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
        "UNIT": Value_WithUnit(1, unit="V"),
        "VARIANT": Value_FromVariants(220, variants=[220, 380]),
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
