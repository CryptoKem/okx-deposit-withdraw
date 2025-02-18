from core.exchanges.okx import Okx
from core.exchanges.binance import Binance
from models.account import Account


class Exchanges:
    """
    Класс для работы с биржами. Инициализирует все биржи.
    При создании новых бирж, импортируйте в данный модуль и инициализируйте в этом классе.
    """
    def __init__(self, account: Account) -> None:
        self.okx = Okx(account)
        self.binance = Binance(account)