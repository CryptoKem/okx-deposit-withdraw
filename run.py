import datetime

from loguru import logger

from config import config, Chains, Tokens
from core.bot import Bot
from core.onchain import Onchain
from core.excel import Excel
from models.account import Account
from utils.logging import init_logger, send_telegram_message
from utils.utils import random_sleep, get_accounts, generate_password, get_price_token, shuffle_account, \
    get_multiplayer


def main():
    """ Основная функция """
    # Инициализация консоли и логгера
    init_logger()
    # Получаем список аккаунтов из файлов
    accounts = get_accounts()

    if not any([config.okx_api_key_main, config.okx_secret_key_main, config.okx_passphrase_main]):
        logger.warning("Не указаны ключи для работы с OKX, не будут работать методы OKX")

    if not any([config.binance_api_key, config.binance_secret_key]):
        logger.warning("Не указаны ключи для работы с Binance, не будут работать методы Binance")

    # перебираем профили в цикле
    for i in range(config.cycle):

        # получаем список аккаунтов для работы
        accounts_for_work = schedule_and_filter(accounts)
        # перемешиваем аккаунты если включен режим случайного выбора
        shuffle_account(accounts_for_work)

        # Перебираем аккаунты
        for account in accounts_for_work:
            # передаем аккаунт в функцию worker
            worker(account)
            # Пауза между профилями
            random_sleep(*config.pause_between_profile)

        logger.success(f'Цикл {i + 1} завершен, обработано {len(accounts_for_work)} аккаунтов')
        logger.info(f'Ожидание перед следующим циклом ~{config.pause_between_cycle[1]} секунд')

        # Пауза между циклами
        random_sleep(*config.pause_between_cycle)


def worker(account: Account) -> None:
    """
    Функция Воркера, который создает бота, передает ему аккаунт и вызывает функции активностей передавая туда бота.
    :param account: аккаунт
    :return: None
    """
    # Создаем бота, если в конфиге включен is_browser_run, то будет запущен браузер
    try:
        with Bot(account) as bot:
            # Вызываем функцию activity и передаем в нее бота
            activity(bot)
            # сюда по необходимости добавляем другие функции с активностями
    except Exception as e:
        logger.critical(f"{account.profile_number} Ошибка при инициализации Bot: {e}")


def schedule_and_filter(accounts: list[Account]) -> list[Account]:
    """
    Функция для фильтрации аккаунтов по времени и дополнительной логике,
    чтобы пропускать те аккаунты, которые не нужно запускать.
    Перебирает аккаунты через фильтры и возвращает новый список аккаунтов для работы.
    :param accounts: список аккаунтов
    :return: список аккаунтов для работы
    """


    # если фильтрация аккаунтов не включена, возвращаем все аккаунты
    if not config.is_schedule:
        return accounts

    # список аккаунтов для работы
    accounts_for_work = []

    # подключение к таблице со статистикой, без аккаунта
    excel = Excel(file='report.xlsx')
    # получаем общую статистику
    swap_counters = excel.get_counters('Swap')
    average_counter = sum(swap_counters) / len(swap_counters)

    # определяем крайнюю дату для последней транзакции
    limit_date = datetime.datetime.now() - datetime.timedelta(days=5)
    limit_swap_counter = 10

    # перебираем аккаунты
    for account in accounts:
        # подключаем аккаунт к таблице
        excel.connect_account(account)

        # проверяем статус профиля в таблице
        status = excel.get_counter('Status')
        if status != 'Work':
            continue

        # получаем статистику по аккаунту
        swap_counter = excel.get_counter('Swap')

        # если количество транзакций больше лимита, пропускаем.
        if swap_counter >= limit_swap_counter:
            continue

        # если количество транзакций больше среднего, пропускаем.
        if swap_counter > average_counter:
            continue

        # если последняя транзакция была недавно, пропускаем.
        last_trans = excel.get_date('Tx Date')
        if last_trans > limit_date:
            continue

        # если аккаунт прошел все фильтры, добавляем его в список для работы
        accounts_for_work.append(account)

    logger.info(f"Выбрано {len(accounts_for_work)} аккаунтов для работы")


    # возвращаем список аккаунтов для работы
    return accounts_for_work



def activity(bot: Bot):
    """
    Функция для работы с ботом, описываем логику активности бота.
    :param bot: бот
    :return: None
    """
    bot.ads.open_url('google.com')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.warning('Программа завершена вручную')
