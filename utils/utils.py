from __future__ import annotations

import functools
import os
import random
import secrets
import string
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Any

import requests
from eth_typing import ChecksumAddress
from web3 import Web3
from loguru import logger

from config.settings import config
from core.excel import Excel
from models.account import Account


def shuffle_account(accounts: list[Account]) -> None:
    """
    Перемешивает аккаунты
    :param accounts: список аккаунтов
    :return: None
    """
    if config.is_random:
        random.shuffle(accounts)


def send_telegram_message(message: str) -> None:
    """
    Отправляет сообщение в телеграм
    :param message: текст сообщения
    :return: None
    """
    url = f'https://api.telegram.org/bot{config.bot_token}/sendMessage'
    params = {'chat_id': config.chat_id, 'text': message}
    requests.get(url, params=params)


def get_accounts() -> list[Account]:
    """
    Получает аккаунты из файла в зависимости от настроек в config
    :return: генератор аккаунтов
    """
    if config.accounts_source == 'excel':
        accounts_raw_data = get_from_excel()
    else:
        accounts_raw_data = get_accounts_from_txt()

    # Определяем количество аккаунтов
    length = len(accounts_raw_data[0])
    # Заполняем списки до нужной длины
    combined_data = filler(length, *accounts_raw_data)
    logger.info(f"Извлечено {length} аккаунтов")

    accounts = []

    # ленивый генератор аккаунтов
    for profile_number, address, password, private_key, seed, proxies in combined_data:
        accounts.append(Account(profile_number, address, password, private_key, seed, proxies))

    return accounts


def get_from_excel() -> tuple[list[str], list[str], list[str], list[str], list[str], list[str]]:
    """
    Получает аккаунты из excel файла
    :return: кортеж списков аккаунтов
    """
    excel = Excel(file='accounts.xlsx')
    # Получаем данные из excel файла
    profile_numbers = excel.get_column("Profile Number")
    passwords = excel.get_column("Password")
    addresses = excel.get_column("Address")
    seeds = excel.get_column("Seed")
    private_keys = excel.get_column("Private Key")
    proxies = excel.get_column("Proxy")
    return profile_numbers, addresses, passwords, private_keys, seeds, proxies


def get_accounts_from_txt() -> tuple[list[str], list[str], list[str], list[str], list[str], list[str]]:
    """
    Достает данные из файлов и возвращает список аккаунтов
    :return: кортеж списков аккаунтов
    """
    # Получаем данные из файлов
    profile_numbers = get_list_from_file("profile_numbers.txt")
    passwords = get_list_from_file("passwords.txt")
    addresses = get_list_from_file("addresses.txt")
    private_keys = get_list_from_file("private_keys.txt")
    seeds = get_list_from_file("seeds.txt")
    proxies = get_list_from_file("proxies.txt")
    return profile_numbers, addresses, passwords, private_keys, seeds, proxies


def filler(length: int, *_args: tuple[list]) -> list[tuple[Any]]:
    """
    Заполняет список до нужной длины
    :param length: длина
    :param _args: список
    :return: заполненный список
    """
    new_args = []
    for arg in _args:
        if not arg:
            arg = [None] * length
        elif len(arg) < length:
            if len(arg) != 0:
                logger.warning('Проверьте файлы с данными, длина списков не совпадает')
            arg += [None] * (length - len(arg))
        new_args.append(arg)
    return list(zip(*new_args))


def get_list_from_file(
        name: str,
        check_empty: bool = False,
) -> list[str]:
    """
    Get list from file
    :param name: название файла с указанием расширения, файл должен находиться в папке config/data
    :param check_empty: проверять ли файл на пустоту
    :return: список строк из файла
    """
    file_path = os.path.join(config.PATH_DATA, name)

    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}, создали пустой файл")
        with open(file_path, "w") as file:
            file.write("")

    if check_empty and os.stat(file_path).st_size == 0:
        logger.error(f"Файл пустой: {file_path}")
        exit(1)

    with open(file_path, "r") as file:
        return file.read().splitlines()


def random_sleep(min_delay: float = 0.5, max_delay: float = 1.5) -> None:
    """
    Sleep random time
    :param min_delay: минимальное время задержки
    :param max_delay: максимальное время задержки
    :return: None
    """
    # если передали только min задержку, то max будет 10% больше
    if min_delay > max_delay:
        max_delay = min_delay * 1.1

    delay = random.uniform(min_delay, max_delay)  # Генерируем случайное число
    time.sleep(delay)  # Делаем перерыв


def generate_password(length_min: int = 25, length_max: int = 35) -> str:
    """
    Генератор случайного пароля
    :param length_min: минимальная длина пароля
    :param length_max: максимальная длина пароля
    :return:
    """
    length = secrets.randbelow(length_max - length_min + 1) + length_min  # Генерируем случайную длину пароля

    # Определяем наборы символов
    all_characters = [string.ascii_uppercase, string.ascii_lowercase, string.digits, string.punctuation]

    # Обеспечиваем наличие хотя бы одного символа каждого типа
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation)
    ]

    while len(password) < length:
        characters = secrets.choice(all_characters)
        password.append(secrets.choice(characters))

    # Перемешиваем пароль, чтобы сделать его менее предсказуемым
    random.shuffle(password)

    return ''.join(password)


def write_text_to_file(path: str, text: str) -> None:
    """
    Write string to file
    :param path: название файла
    :param text: текст
    """
    with open(path, "a") as file:
        file.write(text + "\n")


def get_response(
        url: str,
        params: Optional[dict] = None,
        proxies: Optional[dict] = None,
        attempts: int = 3,
        return_except: bool = True) -> Optional[dict]:
    """
    Делает get запрос и возвращает json из ответа
    :param url: ссылка для запроса
    :param params: параметры запроса
    :param proxies: прокси для запроса
    :param attempts: количество попыток
    :param return_except: возвращать ли исключение
    :return: json из ответа
    """
    response = None
    proxies = prepare_proxy_requests(proxies)
    for _ in range(attempts):
        try:
            response = requests.get(url, params=params, proxies=proxies)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            error_text = f"Ошибка get запроса, {url} {params} - {e}"

            # Добавляем текст ответа, если он есть
            if response is not None and hasattr(response, 'text'):
                error_text += f"\nОтвет сервера: {response.text[:500]}..." if len(
                    response.text) > 500 else f"\nОтвет сервера: {response.text}"

            logger.error(error_text)

    if return_except:
        error_msg = f"Ошибка get запроса, {url} {params}"
        if response is not None and hasattr(response, 'text'):
            error_msg += f"\nОтвет сервера: {response.text[:500]}..." if len(
                response.text) > 500 else f"\nОтвет сервера: {response.text}"
        raise Exception(error_msg)

    return None


def to_checksum(address: Optional[str | ChecksumAddress]) -> ChecksumAddress:
    """
    Преобразует адрес в checksum формат
    :param address: адрес
    :return: адрес в checksum формате
    """
    if address and isinstance(address, str):
        address = Web3.to_checksum_address(address)
    return address

def get_price_token(symbol: str, proxy: str | None = None) -> float:
    """
    Получает цену токена c binance по запросу к API https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT.
    :param symbol: тикер токена (например, ETH)
    :return: цена токена в USDT
    """
    # todo: добавить поддержку прокси
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}USDT"
    response = get_response(url, proxies=proxy)
    return float(response["price"])


def get_multiplayer(min_mult: float = 1.02, max_mult: float = 1.05) -> float:
    """
    Получает множитель для рандомизации чисел. 1.00 =100%, 1.05 = 105%, 0.05 = 5%
    :return: множитель
    """
    return random.uniform(min_mult, max_mult)


def timeout(timeout):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                return future.result(timeout=timeout)

        return wrapper

    return decorator


def prepare_proxy_http(proxy: str) -> Optional[str]:
    """
    Подготавливает прокси для использования в запросах http. Из строки вида "ip:port:login:password" делает строку
    вида "http://login:password@ip:port".
    :param proxy: строка прокси
    :return: прокси для использования в http
    """
    if not proxy:
        return None
    proxy_args = proxy.split(":")
    if len(proxy_args) != 4:
        logger.error("Неверный формат прокси, укажите в формате 'ip:port:login:password'")
        raise ValueError("Неверный формат прокси")
    ip, port, login, password = proxy_args
    return f'http://{login}:{password}@{ip}:{port}'

def prepare_proxy_requests(proxy: str | None) -> dict:
    """
    Подготавливает прокси для использования в запросах библиотеки requests.
    Из строки вида "ip:port:login:password" делает словарь
    с ключами 'http' и 'https'.
    :param proxy: строка прокси
    :return: словарь прокси
    """
    if not proxy:
        return {}

    proxy = prepare_proxy_http(proxy)
    return {
        'http': proxy,
        'https': proxy
    }

def get_user_agent() -> str:
    """
    Получает случайный user-agent из файла user_agents.txt
    :return: user-agent
    """
    user_agents = get_list_from_file("user_agents.txt")
    return random.choice(user_agents)