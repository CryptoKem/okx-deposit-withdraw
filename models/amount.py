from __future__ import annotations

from decimal import Decimal

from web3.types import Wei


class Amount:
    """
    Класс для хранения информации о сумме токенов.

    Для всех классических операций выбирайте ether.

    Для точных операций с wei, используйте wei.

    Для максимально точных операций используйте ether_decimal, но имейте в виду, что это тип данных Decimal.

    Объекты класса Amount можно складывать, вычитать, умножать, делить, находить остаток от деления, возводить в степень вместе
    с другими объектами класса Amount, int, float.
    Объекты класса Amount можно сравнивать между собой, с int, float.

    Атрибуты:

    - wei - количество токенов в wei, минимальная единица измерения
    - ether - количество токенов в ether, в человеческом формате
    - ether_decimal - количество токенов в ether, в формате Decimal, для точных операций
    """

    wei: int | Wei
    ether: float
    ether_decimal: Decimal

    def __init__(self, amount: int | float | Decimal | Wei, decimals: int = 18, wei: bool = False):
        """
        :param amount: сумма токенов в wei или обычном формате
        :param decimals: количество знаков после запятой, по умолчанию 18
        :param wei: указывайте True, если сумма в amount указана в wei (длинное число)
        """
        if wei:
            self.wei = int(amount)
            self.ether_decimal = Decimal(str(amount)) / 10 ** decimals
            self.ether = float(self.ether_decimal)
        else:
            self.wei = int(amount * 10 ** decimals)
            self.ether_decimal = Decimal(str(amount))
            self.ether = float(self.ether_decimal)

        self.decimals = decimals

    def __str__(self) -> str:
        return f'{self.ether}'

    def __add__(self, other: Amount | int | float) -> Amount:
        """
        Сложение двух Amount или сложение Amount с int, float.

        Если слагаемые Amount и имеют разные decimals, то возникнет ошибка.

        При сложении Amount с Amount, сложение будет происходить в wei и результат будет с тем же decimals,
        что и у слагаемых.'

        При сложении Amount с int, float, сложение будет происходить в ether, с точностью float, результат будет
        с тем же decimals, что и у слагаемого Amount.

        Для точных операций используйте ether_decimal.

        :param other: Amount, int, float
        :return: Amount
        """
        if isinstance(other, Amount):
            if self.decimals != other.decimals:
                raise ValueError('Ошибка сложения двух Amount, разное количество знаков после запятой')
            return Amount(self.wei + other.wei, wei=True, decimals=self.decimals)
        if isinstance(other, int) or isinstance(other, float):
            return Amount(self.ether + other, decimals=self.decimals)

        raise ValueError(
            'Ошибка сложения Amount с другим типом данных, сложение возможно только с Amount, int, float')

    def __sub__(self, other: Amount | int | float) -> Amount:
        """
        Вычитание двух Amount или вычитание Amount с int, float.

        Если вычитаемые Amount и имеют разные decimals, то возникнет ошибка.

        При вычитании Amount с Amount, вычитание будет происходить в wei и результат будет с тем же decimals,
        что и у вычитаемых.

        При вычитании Amount с int, float, вычитание будет происходить в ether, с точностью float, результат будет
        с тем же decimals, что и у вычитаемого Amount.

        Для точных операций используйте ether_decimal.
        :param other: Amount, int, float
        :return: Amount
        """
        if isinstance(other, Amount):
            if self.decimals != other.decimals:
                raise ValueError('Ошибка вычитания двух Amount, разное количество знаков после запятой')
            return Amount(self.wei - other.wei, wei=True, decimals=self.decimals)
        if isinstance(other, int) or isinstance(other, float):
            return Amount(self.ether - other, decimals=self.decimals)

        raise ValueError(
            'Ошибка вычитания Amount с другим типом данных, вычитание возможно только с Amount, int, float')

    def __mul__(self, other: Amount | int | float) -> Amount:
        """
        Умножение двух Amount или умножение Amount на int, float.

        Если множители Amount и имеют разные decimals, то возникнет ошибка.

        При умножении Amount на Amount, умножение будет происходить в ether c ether, с точностью float
        и результат будет с тем же decimals, что и у множителей.

        При умножении Amount на int, float, умножение будет происходить в ether, с точностью float, результат будет
        с тем же decimals, что и у множителя Amount.

        Для точных операций используйте ether_decimal.

        :param other: Amount, int, float
        :return: Amount
        """
        if isinstance(other, Amount):
            if self.decimals != other.decimals:
                raise ValueError('Ошибка умножения двух Amount, разное количество знаков после запятой')
            return Amount(self.ether * other.ether, decimals=self.decimals)
        if isinstance(other, int) or isinstance(other, float):
            return Amount(self.ether * other, decimals=self.decimals)

        raise ValueError(
            'Ошибка умножения Amount с другим типом данных, умножение возможно только с Amount, int, float')

    def __truediv__(self, other: Amount | int | float) -> Amount:
        """
        Деление двух Amount или деление Amount на int, float.

        Если делители Amount и имеют разные decimals, то возникнет ошибка.

        При делении Amount на Amount, деление будет происходить в wei c wei, результат будет с тем же
        decimals, что и у делителей.

        При делении Amount на int, float, деление будет происходить в ether, с точностью float, результат будет
        с тем же decimals, что и у делителя Amount.

        Для точных операций используйте ether_decimal.

        :param other: Amount, int, float
        :return: Amount
        """
        if isinstance(other, Amount):
            if self.decimals != other.decimals:
                raise ValueError('Ошибка деления двух Amount, разное количество знаков после запятой')
            return Amount(self.wei / other.wei, wei=True, decimals=self.decimals)

        elif isinstance(other, int) or isinstance(other, float):
            return Amount(self.ether / other, decimals=self.decimals)

        raise ValueError(
            'Ошибка деления Amount с другим типом данных, деление возможно только с Amount, int, float')

    def __mod__(self, other: Amount | int | float) -> Amount:
        """
        Нахождение остатка от деления двух Amount или нахождение остатка от деления Amount на int, float.

        Если делители Amount и имеют разные decimals, то возникнет ошибка.

        При нахождении остатка от деления Amount на Amount, нахождение остатка будет происходить в wei c wei,
        результат будет с тем же decimals, что и у делителей.

        При нахождении остатка от деления Amount на int, float, нахождение остатка будет происходить в ether,
        с точностью float, результат будет с тем же decimals, что и у делителя Amount.

        Для точных операций используйте ether_decimal.

        :param other: Amount, int, float
        :return: Amount
        """
        if isinstance(other, Amount):
            if self.decimals != other.decimals:
                raise ValueError(
                    'Ошибка нахождения остатка от деления двух Amount, разное количество знаков после запятой')
            return Amount(self.wei % other.wei, wei=True, decimals=self.decimals)
        elif isinstance(other, int) or isinstance(other, float):
            return Amount(self.ether % other, decimals=self.decimals)

        raise ValueError(
            'Ошибка нахождения остатка от деления Amount с другим типом данных, операция возможна только с Amount, int, float')

    def __pow__(self, other: Amount | int | float) -> Amount:
        """
        Возведение Amount в степень.

        Если Amount и степень имеют разные decimals, то возникнет ошибка.

        При возведении Amount в степень Amount, возведение будет происходить в ether c ether, результат будет с тем же
        decimals, что и у Amount.

        При возведении Amount в степень int, float, возведение будет происходить в ether, с точностью float, результат\
        будет с тем же decimals, что и у Amount.

        Для точных операций используйте ether_decimal.
        :param other: Amount, int, float
        :return: Amount
        """
        if isinstance(other, Amount):
            if self.decimals != other.decimals:
                raise ValueError(
                    'Ошибка возведения в степень двух Amount, разное количество знаков после запятой')
            return Amount(self.ether ** other.ether, decimals=self.decimals)
        elif isinstance(other, int) or isinstance(other, float):
            return Amount(self.ether ** other, decimals=self.decimals)

        raise ValueError(
            'Ошибка возведения Amount в степень с другим типом данных, операция возможна только с Amount, int, float')

    def __floordiv__(self, other: Amount | int | float) -> Amount:
        """
        Целочисленное деление двух Amount или целочисленное деление Amount на int, float.

        Если Amount и делитель имеют разные decimals, то возникнет ошибка.

        При целочисленном делении Amount на Amount, деление будет происходить в wei c wei, результат будет с тем же
        decimals, что и у Amount.

        При целочисленном делении Amount на int, float, деление будет происходить в ether, с точностью float, результат
        будет с тем же decimals, что и у Amount.

        Для точных операций используйте ether_decimal.
        :param other: Amount, int, float
        :return: Amount
        """
        if isinstance(other, Amount):
            if self.decimals != other.decimals:
                raise ValueError(
                    'Ошибка целочисленного деления двух Amount, разное количество знаков после запятой')
            return Amount(self.wei // other.wei, wei=True, decimals=self.decimals)
        elif isinstance(other, int) or isinstance(other, float):
            return Amount(self.ether // other, decimals=self.decimals)

        raise ValueError(
            'Ошибка целочисленного деления Amount с другим типом данных, операция возможна только с Amount, int, float')

    def __radd__(self, other: Amount | int | float) -> Amount:
        return self + other

    def __rsub__(self, other: Amount | int | float) -> Amount:
        if isinstance(other, Amount):
            return other - self
        elif isinstance(other, int) or isinstance(other, float):
            return Amount(other - self.ether, decimals=self.decimals)
        raise ValueError(
            'Ошибка вычитания Amount с другим типом данных, вычитание возможно только с Amount, int, float')

    def __rmul__(self, other: Amount | int | float) -> Amount:
        return self * other

    def __rtruediv__(self, other: Amount | int | float) -> Amount:
        if isinstance(other, Amount):
            return other / self
        elif isinstance(other, int) or isinstance(other, float):
            return Amount(other / self.ether, decimals=self.decimals)
        raise ValueError(
            'Ошибка деления Amount с другим типом данных, деление возможно только с Amount, int, float')

    def __rmod__(self, other: Amount | int | float) -> Amount:
        if isinstance(other, Amount):
            return other % self
        elif isinstance(other, int) or isinstance(other, float):
            return Amount(other % self.ether, decimals=self.decimals)
        raise ValueError(
            'Ошибка нахождения остатка от деления Amount с другим типом данных, операция возможна только с Amount, int, float')

    def __rpow__(self, other: Amount | int | float) -> Amount:
        return self ** other

    def __rfloordiv__(self, other: Amount | int | float) -> Amount:
        if isinstance(other, Amount):
            return other // self
        elif isinstance(other, int) or isinstance(other, float):
            return Amount(other // self.ether, decimals=self.decimals)
        raise ValueError(
            'Ошибка целочисленного деления Amount с другим типом данных, операция возможна только с Amount, int, float')

    def __eq__(self, other: Amount | int | float) -> bool:
        """
        Сравнение двух Amount или сравнение Amount с int, float.

        Если сравниваемые Amount и имеют разные decimals, то возникнет ошибка.

        При сравнении Amount с Amount, сравнение будет происходить в wei.

        При сравнении Amount с int, float, сравнение будет происходить в ether.

        Для точных операций используйте ether_decimal.
        :param other: Amount, int, float
        :return: bool
        """
        if isinstance(other, Amount):
            if self.decimals != other.decimals:
                raise ValueError('Ошибка сравнения двух Amount, разное количество знаков после запятой')
            return self.wei == other.wei
        if isinstance(other, int) or isinstance(other, float):
            return self.ether == other
        raise ValueError(
            'Ошибка сравнения Amount с другим типом данных, сравнение возможно только с Amount, int, float')

    def __ne__(self, other: Amount | int | float) -> bool:
        return not self == other

    def __lt__(self, other: Amount | int | float) -> bool:
        if isinstance(other, Amount):
            if self.decimals != other.decimals:
                raise ValueError('Ошибка сравнения двух Amount, разное количество знаков после запятой')
            return self.wei < other.wei
        if isinstance(other, int) or isinstance(other, float):
            return self.ether < other
        raise ValueError(
            'Ошибка сравнения Amount с другим типом данных, сравнение возможно только с Amount, int, float')

    def __le__(self, other: Amount | int | float) -> bool:
        return self < other or self == other

    def __gt__(self, other: Amount | int | float) -> bool:
        return not self <= other

    def __ge__(self, other: Amount | int | float) -> bool:
        return not self < other
