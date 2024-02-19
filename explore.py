# DON'T DELETE!
# useful to start smth without pytest and not to run in main script!

from typing import *



class DevTheme:
    __params: Dict[str, Any]

    def __init__(self, params: Dict[str, Any]):
        self.__params = params

    def GET(self, name) -> str:
        pass

    def SET(self, name, value) -> str:
        pass

    def RUN(self, name) -> str:
        pass

    def ON(self) -> str:
        pass

    def OFF(self) -> str:
        pass

    def RST(self) -> str:
        pass
