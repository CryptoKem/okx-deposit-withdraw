from config.chains import Chains
from models.token import Token, TokenTypes
from models.chain import Chain

from models.exceptions import TokenNameError
from utils.utils import to_checksum


class Tokens:
    """
    Класс для хранения токенов, названия переменных должны быть в формате SYMBOL_CHAIN_NAME
    Например: для токена WETH в сети Arbitrum One переменная будет называться WETH_ARBITRUM_ONE
    """

    # токен заглушка для нативного токена в методах onchain
    NATIVE_TOKEN = Token(
        symbol='NATIVE',
        address='0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
        chain=Chains.ETHEREUM,
        decimals=18,
        type_token=TokenTypes.NATIVE
    )

    USDT_ETHEREUM = Token(
        symbol='USDT',
        address='0xdac17f958d2ee523a2206206994597c13d831ec7',
        chain=Chains.ETHEREUM,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    UNI_ETHEREUM = Token(
        symbol='UNI',
        address='0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
        chain=Chains.ETHEREUM,
        type_token=TokenTypes.ERC20,
        decimals=18
    )


    USDT_BSC = Token(
        symbol='USDT',
        address='0x55d398326f99059ff775485246999027b3197955',
        chain=Chains.BSC,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    USDT_POLYGON = Token(
        symbol='USDT',
        address='0xc2132d05d31c914a87c6611c10748aeb04b58e8f',
        chain=Chains.POLYGON,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    USDT_AVALANCHE = Token(
        symbol='USDT',
        address='0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7',
        chain=Chains.AVALANCHE,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    USDT_ZKSYNC = Token(
        symbol='USDT',
        address='0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',
        chain=Chains.ZKSYNC,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    USDT_ARBITRUM_ONE = Token(
        symbol='USDT',
        address='0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        chain=Chains.ARBITRUM_ONE,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    USDT_OP = Token(
        symbol='USDT',
        address='0x94b008aa00579c1307b0ef2c499ad98a8ce58e58',
        chain=Chains.OP,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    USDC_ETHEREUM = Token(
        symbol='USDC',
        address='0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
        chain=Chains.ETHEREUM,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    USDC_BSC = Token(
        symbol='USDC',
        address='0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
        chain=Chains.BSC,
        type_token=TokenTypes.STABLE,
        decimals=18
    )

    USDC_POLYGON = Token(
        symbol='USDC',
        address='0xa8ce8aee21bc2a48a5ef670afcc9274c7bbbc035',
        chain=Chains.POLYGON,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    USDC_AVALANCHE = Token(
        symbol='USDC',
        address='0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
        chain=Chains.AVALANCHE,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    USDC_ZKSYNC = Token(
        symbol='USDC',
        address='0x1d17CBcF0D6D143135aE902365D2E5e2A16538D4',
        chain=Chains.ZKSYNC,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    USDC_ARBITRUM_ONE = Token(
        symbol='USDC',
        address='0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
        chain=Chains.ARBITRUM_ONE,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    USDC_OP = Token(
        symbol='USDC',
        address='0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
        chain=Chains.OP,
        type_token=TokenTypes.STABLE,
        decimals=6
    )

    WETH_ARBITRUM_ONE = Token(
        symbol='WETH',
        address='0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        chain=Chains.ARBITRUM_ONE,
    )

    @classmethod
    def get_token_by_address(cls, address: str) -> Token:
        address = to_checksum(address)
        for token in cls.__dict__.values():
            if isinstance(token, Token):
                if token.address == address:
                    return token
        raise TokenNameError(f'Token with address {address} not found')

    @classmethod
    def get_token_by_symbol(cls, symbol: str, chain: Chain) -> Token:
        """
        Получение токена по символу и сети.
        :param symbol:  символ токена
        :param chain:  объект Chain
        :return:
        """
        symbol_and_chain = f'{symbol.upper()}_{chain.name.upper()}'
        return getattr(cls, symbol_and_chain)

    @classmethod
    def add_token(cls, token: Token):
        setattr(cls, token.symbol, token)
        return token

    @classmethod
    def get_tokens_by_chain(cls, chain: Chain) -> list[Token]:
        """
        Получение списка токенов для сети.
        :param chain: объект Chain
        :return:  список токенов
        """
        tokens = []
        for token in cls.__dict__.values():
            if isinstance(token, Token):
                if token.chain == chain:
                    if token.type_token == TokenTypes.NATIVE:
                        continue
                    tokens.append(token)
        return tokens

    @classmethod
    def get_tokens(cls) -> list[Token]:
        """
        Получение списка всех токенов.
        :return: список токенов
        """
        tokens = []
        for token in cls.__dict__.values():
            if isinstance(token, Token):
                if token.type_token == TokenTypes.NATIVE:
                    continue
                tokens.append(token)
        return tokens
