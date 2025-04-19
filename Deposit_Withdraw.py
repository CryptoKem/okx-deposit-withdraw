
    """ #Вывод c OKX в нативной монете
    balance = bot.onchain.get_balance()
    print(balance)
    if balance < 0.01:
        amount = round(random.uniform(0.00120, 0.00200), 5)
        bot.exchanges.okx.withdraw(token="ETH", amount=amount, chain=bot.chain)
        logger.success("ETH выведены")"""

   """ #Вывод c OKC в $ выражении
    eth_balance = bot.onchain.get_balance()
    eth_price = get_price_token('ETH')
    usd_balance = eth_balance * eth_price
    if usd_balance < 5:
        withdrav_amount = (5 - usd_balance) / eth_price
        bot.exchanges.okx.withdraw(token='ETH', amount=withdrav_amount, chain=bot.chain)
        logger.success('ETH выведены')
        random_sleep(100,200)"""

"""# Deposit OKX
    sub = bot.excel.get_cell('sub_acc_okx')
    bot.onchain.send_token(to_address=sub, amount=0.003)
    logger.success("OKX deposit отправлен")

    #Смена сети
    onchain_zksync = Onchain(bot.account, Chains.ZKSYNC)
    amount = onchain_zksync.get_balance(token=Tokens.USDT_ZKSYNC)
    onchain_zksync.send_token(amount=amount, to_address=sub, token=Tokens.USDT_ZKSYNC)"""







