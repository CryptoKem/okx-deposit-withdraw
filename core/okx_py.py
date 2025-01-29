from __future__ import annotations

from typing import Literal, Optional

from config import config

import okx.Funding as Funding
from loguru import logger

from models.account import Account
from models.amount import Amount
from models.chain import Chain
from models.token import Token
from utils.utils import random_sleep, prepare_proxy_httpx


class OKX:
    """
    Класс для работы с биржей OKX.
    """

    def __init__(self, account: Account) -> None:
        self.account = account
        self._chains: Optional[list[str]] = None


        self.funding_api = Funding.FundingAPI(
            config.okx_api_key_main,
            config.okx_secret_key_main,
            config.okx_passphrase_main,
            flag="0",
            debug=False,
            proxy=prepare_proxy_httpx(config.okx_proxy)
        )

        try:
            self.funding_api.get_currencies()
            logger.info(f"{self.account.profile_number} Подключение к OKX прошло успешно")
        except Exception as error:
            logger.warning(f"Не удалось подключиться к OKX, возможно нужно указать прокси для биржи в settings: {error}, запускаем без OKX.")



    def get_chains(self) -> list[str]:
        """
        Возвращает список сетей, которые поддерживает биржа OKX.
        :return: cписок сетей.
        """
        if not self._chains:
            response = self.funding_api.get_currencies()
            data = response.get("data")
            if response.get("code") != "0":
                logger.error(
                    f"{self.account.profile_number} Не удалось получить список токенов: {response.get('msg')}")
            chains = set()
            for chain in data:
                if chain.get("chain"):
                    chain = chain.get("chain").split("-")[1]
                    chains.add(f"'{chain}'")
            self._chains = list(chains)
        return self._chains


    def check_chain(self, chain: Chain | str) -> bool:
        """
        Проверяет, поддерживает ли биржа OKX сеть. Проверка происходит по названию сети без учета регистра.
        :param chain: объект сети Chain или строка с названием сети
        :return: True если сеть поддерживается, иначе False
        """
        if isinstance(chain, Chain):
            if not chain.okx_name:
                logger.warning(f"{self.account.profile_number} [OKX] -> у сети {chain.name} нет названия для OKX")
                return False
            chain = chain.okx_name
        chains = self.get_chains()
        chains = [chain.lower() for chain in chains]
        return chain.lower() in chains




    def withdraw(
            self,
            token: Token | str,
            amount: int | float | Amount,
            chain: Chain | Literal['DYDX', 'l', 'zkSync Era', 'Wax', 'ERC20', 'Ethereum Classic',
            'Casper', 'Tezos', 'NULS', 'Harmony', 'Theta', 'Litecoin', 'BitcoinCash',
            'Elrond', 'Conflux', 'Mina', 'Zilliqa', 'MIOTA', 'Cosmos', 'CELO',
            'Ontology', 'Polygon (Bridged)', 'BSC', 'Khala', 'N3', 'TON',
            'Polygon', 'OKTC', 'AELF', 'Metis (Token Transfer)', 'PlatON',
            'FLOW', 'Linea', 'Avalanche X', 'Aptos', 'Fantom', 'Cortex',
            'BRC20', 'Enjin Relay Chain', 'Flare', 'Siacoin', 'Layer 3', 'Moonbeam',
            'Acala', 'Lisk', 'IOST', 'OASYS', 'Arweave', 'Starknet', 'EthereumPoW',
            'NEAR', 'Klaytn', 'Stellar Lumens', 'TRC20', 'SUI', 'Avalanche C',
            'Endurance Smart Chain', 'Cardano', 'ZetaChain', 'FEVM', 'Dogecoin',
            'Terra Classic', 'CORE', 'ICON', 'Algorand', 'INJ', 'Moonriver', 'Crypto',
            'Scroll', 'Dfinity', 'Chiliz Chain', 'X Layer', 'Optimism (V2)', 'Celestia',
            'Chiliz 2.0 Chain', 'Base', 'Bitcoin', 'Kadena', 'EOS', 'Optimism',
            'Digibyte', 'Hedera', 'Nano', 'Polkadot', 'Terra', 'Venom', 'Bitcoin SV',
            'MERLIN Network', 'Solana', 'Gravity Alpha Mainnet', 'CFX_EVM', 'Lightning',
            'Chia', 'Terra Classic (USTC)', 'Kusama', 'Ripple', 'Metis', 'Ravencoin',
            'Filecoin', 'Arbitrum One', 'Astar', 'Quantum', 'Ronin'],
            address: Optional[str] = None
    ) -> None:
        """
        Вывод средств с биржи OKX, на адрес профиля или указанный адрес. После вывода ожидает подтверждения транзакции.
        :param token: токен для вывода, можно передать объект Token или строку с названием токена
        :param amount: количество токенов для вывода, можно передать объект Amount или число
        :param chain: сеть вывода, можно передать объект Chain или строку с названием сети
        :param address: адрес для вывода, если не указан, то на адрес профиля
        :return: None
        """

        if not address:
            address = self.account.address

        if isinstance(chain, Chain):
            if not chain.okx_name:
                logger.error(f"{self.account.profile_number} [OKX] Вывод невозможен, у сети {chain.name} нет названия для OKX")
                return
            chain = chain.okx_name

        if isinstance(token, Token):
            token = token.symbol

        if isinstance(amount, Amount):
            amount = amount.ether

        token_with_chain = token + "-" + chain
        fee = self._get_withdrawal_fee(token, token_with_chain)

        try:
            logger.info(f'{self.account.profile_number}: Выводим с okx {amount} {token} на адрес {address}')
            response = self.funding_api.withdrawal(
                ccy=token,
                amt=amount,
                dest=4,
                toAddr=address,
                fee=fee,
                chain=token_with_chain,
            )
            if response.get("code") != "0":
                raise Exception(
                    f'{self.account.profile_number}: Не удалось вывести {amount} {token}: {response.get("msg")}')
            tx_id = response.get("data")[0].get("wdId")
            self._wait_confirm(tx_id)
            logger.info(f'{self.account.profile_number}: Успешно выведено {amount} {token}')
        except Exception as error:
            logger.error(f'{self.account.profile_number}: Не удалось вывести {amount} {token}: {error} ')
            raise error

    def _get_withdrawal_fee(self, token: str, token_with_chain: str):
        """
        Получение комиссии за вывод
        :param token: название токена
        :param token_with_chain: айди токен-сеть
        :return:
        """
        response = self.funding_api.get_currencies(token)
        for network in response.get("data"):
            if network.get("chain") == token_with_chain:
                return network.get("minFee")

        logger.error(
            f"{self.account.profile_number} не могу получить сумму комиссии, проверьте значения symbolWithdraw и network")
        return 0

    def _wait_confirm(self, tx_id: str) -> None:
        """
        Ожидание подтверждения транзакции вывода с OKX
        :param tx_id: id транзакции вывода
        :return: None
        """
        for _ in range(30):
            tx_info = self.funding_api.get_deposit_withdraw_status(wdId=tx_id)
            if tx_info.get("code") == "0":
                if 'Withdrawal complete' in tx_info.get("data")[0].get("state"):
                    logger.info(f"{self.account.profile_number} Транзакция {tx_id} завершена")
                    return
            random_sleep(10)
        logger.error(f"{self.account.profile_number} Ошибка транзакция {tx_id} не завершена")
        raise Exception(f"Транзакция {tx_id} не завершена")
