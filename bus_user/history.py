from typing import *


# =====================================================================================================================
class HistoryIO:
    history: list[Tuple[str, list[str]]] = None

    def __init__(self):
        self.history = []

    def count(self) -> int:
        return len(self.history)

    def clear(self) -> None:
        self.history.clear()

    def as_dict(self) -> dict[str, list[str]]:
        return dict(self.history)

    # ADD =============================================================================================================
    def add_input(self, data: str) -> None:
        self.history.append((data, []))

    def add_output(self, data: Union[str, list[str]]) -> None:
        if not self.history:
            self.add_input("")

        output_last = self.history[-1][1]
        if isinstance(data, (tuple, list, )):
            # LIST
            output_last.extend(data)
        else:
            # SINGLE
            output_last.append(data)

    def add_io(self, data_i: str, data_o: Union[str, list[str]]) -> None:
        self.add_input(data_i)
        self.add_output(data_o)

    def add_history(self, history: 'HistoryIO') -> None:
        for data_i, data_o in history.history:
            self.add_input(data_i)
            self.add_output(data_o)

    # CHECK ===========================================================================================================
    def check_equal_io(self) -> bool:
        """
        created specially for testing UART bus when shorted Rx+Tx
        """
        for data_i, data_o in self.history:
            if not (len(data_o) == 1 and data_o[0] == data_i):
                return False
        return True

    # LAST ============================================================================================================
    @property
    def last_input(self) -> str:
        if self.history:
            return self.history[-1][0]
        return ""

    @property
    def last_output(self) -> str:
        if self.history and self.history[-1][-1]:
            return self.history[-1][-1][-1]
        return ""

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


# =====================================================================================================================
