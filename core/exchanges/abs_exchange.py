from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from loguru import logger

from models.account import Account
from models.amount import Amount
from models.chain import Chain
from models.token import Token

from models.withdraw import WithdrawData

# класс для обмена валют
class AbsExchange(ABC):
    """
    Абстрактный класс для работы с биржами. Валидирует наличие методов и их аргументов.
    Используется как основа для создания классов бирж, наследуемых от него в формате: class NewExchange(AbsExchange).
    Должны быть обязательно реализованы методы с аннотацией @abstractmethod.
    """
    _chains: list[str] | set[str] = []

    @abstractmethod
    def __init__(self, account: Account) -> None:
        """
        Инициализация биржи. В конструкторе должен быть передан объект аккаунта.
        Чтобы методы могли использовать адрес кошелька из аккаунта для вывода средств.
        """
        self.account = account
        pass

    @abstractmethod
    def get_chains(self) -> list:
        """
        Реализуйте метод получения поддерживаемых блокчейнов биржей. Выведите в терминал список и верните его
        как список строк. Используйте множества, чтобы избежать дубликатов при сборе данных.
        У каждой биржи уникальные названия сетей, поэтому метод должен быть реализован в каждом классе биржи
        для удобного запроса списка сетей, для последующего заполнения Chains.
        У всех бирж есть API позволяющий получить список сетей или токенов, которые они поддерживают.
        :return: список поддерживаемых сетей и токенов
        """
        pass

    @abstractmethod
    def withdraw(
            self,
            *,
            token: Token | str,
            amount: Amount | int | float,
            chain: Chain | str,
            address: Optional[str] = None
    ) -> None:
        """
        Метод вывода токенов с биржи. В реализации необходимо реализовать валидацию входных данных,
        извлечение данных из объектов токена, количества и сети, подготовка данных для вывода,
        отправка запроса на вывод и ожидание завершения вывода.
        Подпись данных для вывода, методы отправки запроса и метод проверки статуса должны быть
        реализованы отдельно и вызываться в этом методе.
        :param token: тикер токена
        :param chain: сеть в корректном формате для конкретной биржи
        :param amount: количество
        :param address: адрес получателя, если не указан, то на адрес в account
        """
        pass

    @abstractmethod
    def _wait_until_withdraw_complete(self, withdraw_id: str, timeout: int = 30) -> None:
        """
        Метод должен запрашивать либо список всех выводов с биржи, либо конкретный вывод по идентификатору,
        и ожидать завершения вывода. У многих бирж собственные статусы выводов, выясните в документации,
        делайте паузы между запросами от 10 секунд.
        :param withdraw_id: идентификатор вывода
        :param timeout: количество попыток с интервалом в 10 секунд
        """
        pass

    def _validate_inputs(
            self,
            token: Token | str,
            amount: Amount | int | float,
            chain: Chain | str,
            address: Optional[str]
    ) -> WithdrawData:
        """
        Извлекает данные из объектов, проверяет входные данные на корректность и возвращает объект данных для вывода.
        :param token: объект токена
        :param amount: объект количества
        :param chain: объект сети
        :param address: адрес получателя
        :return: объект данных для вывода
        """

        if not address:
            address = self.account.address

        if isinstance(token, Token):
            token = token.symbol

        if isinstance(amount, Amount):
            amount = amount.ether

        chain = self._get_chain_name(chain)

        withdraw_data = WithdrawData(
            token=token,
            amount=amount,
            chain=chain,
            address=address
        )

        if not withdraw_data.is_valid:
            logger.error(f'{self.account.profile_number} [{self.__class__.__name__}] Переданы некорректные аргументы в withdraw(): {withdraw_data}')
            raise ValueError(f'Переданы некорректные аргументы в {self.__class__.__name__}.withdraw()')

        return withdraw_data

    def _get_chain_name(self, chain: Chain | str) -> str | None:
        """
        Возвращает имя для биржи из объекта сети. Если нет, логирует ошибку.
        Работает по разному для разных классов бирж. У объекта сети должно быть поле с названием сети для биржи
        в формате: binance_name, okx_name, bybit_name и т.д.
        :param chain: объект сети
        :return: имя сети для биржи
        """
        if isinstance(chain, str):
            return chain

        if isinstance(chain, Chain):
            # получаем название биржи из имени класса
            exchange_name = self.__class__.__name__.lower()
            # ищем название сети для биржи в объекте сети
            chain_name = getattr(chain, f'{exchange_name}_name')

            if chain_name is None:
                logger.error(
                    f'{self.account.profile_number} [{self.__class__.__name__}] Вывод невозможен, у сети {chain.name} нет названия для')
            return chain_name

