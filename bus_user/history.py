from typing import *


# =====================================================================================================================
TYPE__IO = tuple[str, list[str]]


# =====================================================================================================================
# TODO:
#   USE OBJECTS instead of tuples? + internal add+read
#   1. use deque with objects Write Read WEol REol None(not used)?
#   2. add top(n=10)
#   if when writeLine - always readLines?


class HistoryIO:
    history: list[TYPE__IO] = []

    def __init__(self):
        self.history = []

    def count(self) -> int:
        """
        count requests
        """
        return len(self.history)

    def clear(self) -> None:
        self.history.clear()

    # ADD =============================================================================================================
    def add_input(self, data: str) -> None:
        self.history.append((data, []))

    def add_output(self, data: Union[str, list[str]]) -> None:
        if not self.history:
            self.add_input("")

        if isinstance(data, (tuple, list, )):
            self.last_outputs.extend(data)
        else:
            # SINGLE
            self.last_outputs.append(data)

    def add_io(self, data_i: str, data_o: Union[str, list[str]]) -> None:
        self.add_input(data_i)
        self.add_output(data_o)

    def add_history(self, history: 'HistoryIO') -> None:
        for data_i, data_o in history.history:
            self.add_input(data_i)
            self.add_output(data_o)

    # LAST ============================================================================================================
    @property
    def last_io(self) -> TYPE__IO | None:
        try:
            return self.history[-1]
        except:
            return None

    @property
    def last_input(self) -> str:
        try:
            return self.last_io[0]
        except:
            return ""

    @property
    def last_outputs(self) -> list[str]:
        try:
            return self.last_io[1]
        except:
            return []

    @property
    def last_output(self) -> str:
        try:
            return self.last_outputs[-1]
        except:
            return ""

    # CHECK ===========================================================================================================
    def check_equal_io(self) -> bool:
        """
        CREATED SPECIALLY FOR
        ---------------------
        testing UART bus when shorted Rx+Tx
        """
        for data_i, data_o in self.history:
            if not (len(data_o) == 1 and data_o[0] == data_i):
                return False
        return True

    # LIST+PRINT ======================================================================================================
    def list_input(self) -> list[str]:
        result = []
        for data_i, data_o in self.history:
            result.append(data_i)
            print(data_i)
        return result

    def list_output(self) -> list[str]:
        result = []
        for data_i, data_o in self.history:
            for line in data_o:
                result.append(line)
                print(line)
        return result

    def print_io(self) -> None:
        name = "print_io"
        print("="*10 + f"{name.upper():=<90}")
        print()
        for data_i, data_o in self.history:
            print(f"{data_i:20}:", end="")
            indent = ""
            if data_o:
                for line in data_o:
                    line = f"{indent}{line}"
                    print(line)
                    indent = " "*20 + ":"
            else:
                print()
        print("="*100)

    def as_dict(self) -> dict[str, list[str]]:
        """not correct if exists same write"""
        return dict(self.history)


# =====================================================================================================================
