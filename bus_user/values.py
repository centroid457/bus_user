from . import *

from typing import *
import time
import re
import logging
import datetime

from object_info import ObjectInfo
from PyQt5.QtCore import QThread

import funcs_aux


# =====================================================================================================================
class Value_NotPassed:
    """
    resolve not passed parameters in case of None value!

    special object used as value to show that parameter was not passed!
    dont pass it directl! keep it only as default parameter in class and in methods instead of None Value!
    it used only in special cases! not always even in one method!!!
    """
    pass
    # @classmethod
    # def __str__(self):
    #     return ""     # it used as direct Class! without any instantiation!


# =====================================================================================================================
class Value_WithUnit:
    """
    used to keep separated value and measure unit
    """
    value: Union[int, float] = 0
    UNIT: str = ""
    SEPARATOR: str = ""

    # TODO: add arithmetic/comparing magic methods like SUM/...
    # TODO: move to funcs_aux

    def __init__(self, value: Union[int, float, Any] = None, unit: str = None, separator: str = None):
        """
        :param value: expecting number (int/float) in any form (str/any other object)!
        """
        # FIXME: create class without INIT! with changeable type!!!
        if value is not None:
            self.value = float(value)
            try:
                if float(value) == int(value):
                    self.value = int(value)
            except:
                pass
        if unit is not None:
            self.UNIT = unit
        if separator is not None:
            self.SEPARATOR = separator

    def __str__(self) -> str:
        return f"{self.value}{self.SEPARATOR}{self.UNIT}"

    def __repr__(self) -> str:
        """
        used as help
        """
        return f"{self.value}'{self.UNIT}'"

    def __eq__(self, other):
        # DONT USE JUST str()=str() separator is not valuable! especially for digital values
        if isinstance(other, Value_WithUnit):
            return (self.value == other.value) and (self.UNIT == other.UNIT)
        else:
            return self.value == other

    def __ne__(self, other):
        return not self == other


# =====================================================================================================================
class Exx__ValueNotInVariants(Exception):
    pass


class Exx__VariantsIncompatible(Exception):
    pass


class Value_FromVariants:
    """
    used to keep separated value and measure unit
    """
    # TODO: move to funcs_aux
    # TODO: combine with Value_WithUnit - just add ACCEPTABLE(*VARIANTS) and rename UNIT just as SUFFIX!

    # SETTINGS -----------------------
    CASE_INSENSITIVE: bool = True
    VARIANTS: List[Any] = None

    # DATA ---------------------------
    __value: Any = Value_NotPassed   # changeable   # TODO: default as first in variant! or pass exact value!

    def __init__(self, value: Union[str, Any] = Value_NotPassed, variants: List[Union[str, Any]] = None, case_insensitive: bool = None):
        """
        :param value: None mean NotSelected/NotSet!
            if you need set None - use string value in any case! 'None'/NONE/none
        """
        # FIXME: need think about None value!
        # settings ---------------
        if case_insensitive is not None:
            self.CASE_INSENSITIVE = case_insensitive
        if variants is not None:
            self.VARIANTS = variants

        # work ---------------
        self._variants_validate()

        if value != Value_NotPassed:
            self.value = value

    def __str__(self) -> str:
        return f"{self.value}"

    def __repr__(self) -> str:
        """
        used as help
        """
        return f"{self.value}{self.VARIANTS}"

    def __eq__(self, other):
        if isinstance(other, Value_FromVariants):
            other = other.value

        # todo: decide is it correct using comparing by str()??? by now i think it is good enough! but maybe add it as parameter
        if self.CASE_INSENSITIVE:
            return (self.value == other) or (str(self.value).lower() == str(other).lower())
        else:
            return (self.value == other) or (str(self.value) == str(other))

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return len(self.VARIANTS)

    def __iter__(self):
        yield from self.VARIANTS

    def __contains__(self, item):
        """
        used to check compatibility
        """
        for variant in self.VARIANTS:
            if self.CASE_INSENSITIVE:
                result = str(variant).lower() == str(item).lower()
            else:
                result = str(variant) == str(item)
            if result:
                return True

        return False

    def _variants_validate(self) -> Optional[NoReturn]:
        if self.CASE_INSENSITIVE:
            real_len = len(set(map(lambda item: str(item).lower(), self.VARIANTS)))
        else:
            real_len = len(set(self.VARIANTS))

        result = real_len == len(self.VARIANTS)
        if not result:
            raise Exx__VariantsIncompatible()

    @property
    def value(self) -> Any:
        return self.__value

    @value.setter
    def value(self, value: Any) -> None:
        for variant in self.VARIANTS:
            if self.CASE_INSENSITIVE:
                result = str(variant).lower() == str(value).lower()
            else:
                result = str(variant) == str(value)
            if result:
                self.__value = variant
                return

        raise Exx__ValueNotInVariants()


# =====================================================================================================================
