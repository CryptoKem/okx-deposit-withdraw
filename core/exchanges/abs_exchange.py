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
    name: str
    _chains: list[str] | set[str] = []

    @abstractmethod
    def __init__(self, account: Account) -> None:
        """
        Инициализация биржи.
        """
        self.account = account
        pass

    @abstractmethod
    def get_chains(self) -> list:
        """
        Печатает в консоль список поддерживаемых сетей и токенов в их корректном формате для конкретной биржи.
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
        Выводит средства с биржи на указанный адрес в указанной сети.
        :param token: тикер токена
        :param chain: сеть в корректном формате для конкретной биржи
        :param amount: количество
        :param to_address: адрес получателя
        """
        pass

    @abstractmethod
    def _wait_until_withdraw_complete(self, withdraw_id: str, timeout: int = 30) -> None:
        """
        Ожидает завершения вывода средств.
        :param withdraw_id: идентификатор вывода
        :param timeout: количество попыток с интервалом в 1 секунду
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
        Проверяет входные данные на корректность.
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

        return withdraw_data

    def _get_chain_name(self, chain: Chain | str) -> str | None:
        """
        Возвращает имя для биржи из объекта сети. Если нет, логирует ошибку.
        Работает по разному для разных классов бирж.
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
                    f"{self.account.profile_number} [{self.name}] Вывод невозможен, у сети {chain.name} нет названия для {self.name}")
            return chain_name

