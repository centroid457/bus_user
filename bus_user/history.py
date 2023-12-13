from typing import *


# =====================================================================================================================
class HistoryIO:
    history: List[Tuple[str, List[str]]] = None

    def __init__(self):
        self.history = []

    def count(self) -> int:
        return len(self.history)

    def clear(self) -> None:
        self.history.clear()

    def as_dict(self) -> Dict[str, List[str]]:
        return dict(self.history)

    # ADD =============================================================================================================
    def add_input(self, data: str) -> None:
        self.history.append((data, []))

    def add_output(self, data: Union[str, List[str]]) -> None:
        if not self.history:
            self.add_input("")

        output_last = self.history[-1][1]
        if isinstance(data, (tuple, list, )):
            output_last.extend(data)
        else:
            output_last.append(data)

    def add_io(self, data_i: str, data_o: Union[str, List[str]]) -> None:
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

    # LIST+PRINT ======================================================================================================
    def list_input(self) -> List[str]:
        result = []
        for data_i, data_o in self.history:
            result.append(data_i)
            print(data_i)
        return result

    def list_output(self) -> List[str]:
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
