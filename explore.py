# DON'T DELETE!
# useful to start smth without pytest and not to run in main script!

from bus_user import *
from typing import *
import time


class Dev(SerialClient_FirstFree_Shorted):
    BAUDRATE: int = 115200
    EOL__SEND = b"\r\n"
    RAISE_CONNECT = False
    LOG_ENABLE = True

    REWRITEIF_READFAILDECODE = 5
    # TIMEOUT__READ: float = 3       # 0.2 is too short!!! dont touch! in case of reading char by char 0.5 is the best!!! 0.3 is not enough!!!

    # def address__validate(self) -> bool | None | NoReturn:
    #     for i in range(5):
    #         self._write('help')
    #         if self.read_line():
    #             break
    #         time.sleep(1)
    #     self.buffers_clear()


dev = Dev()
if dev.connect():
    # for i in range(10):
    #     if dev.write_read__last('stop'):
    #         break
    #     time.sleep(0.5)
    #     print()
    #     print()
    #     print()
    #     print()
    #     print()


    index = 0
    while True:
        index += 1
        load = f"step{index}"
        print(load)
        if not dev.write_read__last(load) == load:
            print(f"FAIL{load=}")
