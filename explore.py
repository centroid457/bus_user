# DON'T DELETE!
# useful to start smth without pytest and not to run in main script!

from bus_user import *


class Dev(SerialClient_FirstFree):
    LOG_ENABLE = True
    EOL__SEND: bytes = b"\n"
    BAUDRATE = 115200


dev = Dev()
assert dev.connect()
print(f"{dev.ADDRESS=}")

print(dev.write_read__last("*:GET NAME"))
# print(dev._write(b"\n"))
