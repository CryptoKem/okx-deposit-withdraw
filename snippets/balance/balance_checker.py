"""Пример проверки баланса во всех сетях всех токенов из конфига"""

from loguru import logger

from config import Chains, Tokens
from core.bot import Bot
from core.excel import Excel
from core.onchain import Onchain
from utils.utils import get_price_token


def activity(bot: Bot):
    """
    Функция для работы с ботом, описываем логику активности бота.
    :param bot: инициализированный бот
    """
    prices = {}

    excel = Excel(account=bot.account, file='balances.xlsx')
    excel.set_cell('Address', bot.account.address)

    chains = Chains.get_chains_list()
    for chain in chains:
        chain_instance = Onchain(bot.account, chain)
        tokens = Tokens.get_tokens_by_chain(chain)
        balance = chain_instance.get_balance()
        logger.info(f'Баланс {chain.native_token} на сети {chain.name}: {balance}')
        excel.set_cell(f'{chain.name} {chain.native_token}', balance.ether)
        if not prices.get(chain.native_token, 0):
            price = get_price_token(chain.native_token)
            prices[chain.native_token] = price
        usd_balance = balance.ether * prices[chain.native_token]
        excel.set_cell(f'$ {chain.name} {chain.native_token}', usd_balance)


        for token in tokens:
            balance = chain_instance.get_balance(token=token)

            logger.info(f'Баланс {token.symbol} на сети {chain.name}: {balance}')
            excel.set_cell(f'{chain.name} {token.symbol}', balance.ether)
            if token.type_token != 'stable':
                if not prices.get(token.symbol, 0):
                    price = get_price_token(token.symbol)
                    prices[token.symbol] = price
                usd_balance = balance.ether * prices[token.symbol]
                excel.set_cell(f'$ {chain.name} {token.symbol}', usd_balance)

