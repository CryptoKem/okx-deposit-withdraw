import random

from loguru import logger

from config import Chains
from core.bot import Bot
from core.onchain import Onchain
from utils.utils import random_sleep


def activity(bot: Bot):
    """
    Функция для работы с ботом, описываем логику активности бота.
    :param bot: бот
    :return: None
    """

    chains = [Chains.OP, Chains.ARBITRUM_ONE, Chains.ETHEREUM]
    chain = random.choice(chains)

    onchain_instance = Onchain(bot.account, chain)

    bot.metamask.select_chain(chain)

    bot.ads.open_url('https://superbridge.app/soneium')

    random_sleep(2, 3)
    button_agree = bot.ads.page.get_by_role('button', name='Agree & continue')
    if button_agree.count():
        button_agree.click()

    connect_button = bot.ads.page.get_by_role('button', name='Connect')
    if connect_button.count():
        bot.ads.page.get_by_role('button', name='Connect').first.click()
        bot.ads.page.get_by_text('MetaMask').click()
        bot.metamask.universal_confirm()
        random_sleep(2, 3)

    bot.ads.page.locator('//span[text()="From"]/following-sibling::span').click()

    son_chains = {
        Chains.OP: 'OP Mainnet',  # вписать название сети на сайте
        Chains.ARBITRUM_ONE: 'Arbitrum One',  # вписать название сети на сайте
        Chains.ETHEREUM: 'Ethereum Mainnet'  # вписать название сети на сайте
    }

    random_amount = random.uniform(0.01, 0.1)

    bot.ads.page.get_by_role('heading', name=son_chains[chain]).click()
    if onchain_instance.get_balance().ether < random_amount:
        bot.exchanges.okx.withdraw(
            amount=0.01,  # рандомизировать сумму
            token='ETH',
            chain=chain
        )
    bot.ads.page.get_by_role('textbox').fill(str(random_amount))
    bot.ads.page.get_by_role('button', name='Review bridge').click()
    bot.ads.page.get_by_role('button', name='Continue').click()
    if bot.ads.page.get_by_role('heading',
                                name="Make sure the wallet you're bridging to supports Soneium").count():
        bot.ads.page.locator('#addressCheck').click()
        bot.ads.page.get_by_role('button', name='Continue').click()
    bot.ads.page.get_by_role('button', name='Start').click()
    bot.metamask.universal_confirm(windows=2, buttons=2)

    sol_onchain = Onchain(bot.account, Chains.Soneium)
    balance_before = sol_onchain.get_balance().ether

    for _ in range(60):
        balance_after = sol_onchain.get_balance().ether
        if balance_after > balance_before:
            logger.success('Транзакция прошла')
            bot.excel.increase_counter('Bridge Sonium')
            break
        random_sleep(10, 15)
    else:
        logger.error('Транзакция не прошла')
        raise Exception('Транзакция не прошла')