from loguru import logger
import random

from core.bot import Bot
from utils.utils import random_sleep

"""
реализация автотапалки для https://tap.eclipse.xyz/onboarding/
реализованы сбросы запросов, выключение анимаций, и ускорение setTimeout (уменьшение пауз на сайте)

"""


def disable_animations(bot: Bot):
    """Отключает анимации и скрывает canvas."""
    bot.ads.page.evaluate('''
        let styleSheet = document.createElement('style');
        styleSheet.textContent = `
            * { transition: none !important; animation: none !important; transform: none !important; }
            canvas { display: none !important; }
        `;
        document.head.appendChild(styleSheet);
    ''')
    print('✅ Анимации отключены, canvas скрыт.')


def intercept_requests(route):
    if 'https://tap.eclipse.xyz/api/user/points' in route.request.url:
        if random.random() < 0.5:
            print(f'❌ Саботирован запрос: {route.request.url}')
            route.abort()
        else:
            print(f'✅ Разрешен запрос: {route.request.url}')
            route.continue_()
    else:
        route.continue_()

def override_setTimeout(bot: Bot):
    """Перехватчик для ускорения setTimeout"""
    bot.ads.page.evaluate("""
        window.originalSetTimeout = window.originalSetTimeout ?? window.setTimeout;
        window.setTimeout = (f, t) => {
            if (t === 1000) {
                window.originalSetTimeout(f, 10); // ускорение 1-секундных таймеров
            } else if (t > 3000 && t < 4000) {
                f(); // мгновенное выполнение
            } else {
                window.originalSetTimeout(f, t); // стандартное выполнение
            }
        };
    """)
    print('✅ Перехватчик setTimeout установлен')

def poke_the_cow(bot: Bot):

    bot.ads.open_url('https://tap.eclipse.xyz/', wait_until='load', timeout=50)

    # Если первый вход, жмем 'I agree'
    i_agree_popup = bot.ads.page.locator("""//p[text()='I agree to Eclipse's']/preceding-sibling::div""")
    if bot.ads.wait_result(i_agree_popup, attempts=3):
        i_agree_popup.click()
        bot.ads.page.get_by_role('button', name='Continue').click()

    # Жмем 'I have a Turbo Tap account'
    if bot.ads.wait_result('I have a Turbo Tap account', attempts=3):
        bot.ads.page.get_by_text('I have a Turbo Tap account').click()
        bot.ads.page.get_by_test_id('wallet-icon-backpackeclipse').click()
        backpack_connect_button = bot.ads.page.get_by_test_id('select-hardware-wallet-connect-button')
        bot.backpack.connect(backpack_connect_button)

    # Проверяем подключение кошелька
    if bot.ads.page.get_by_role('button', name='Connect Wallet').count():
        bot.ads.page.get_by_role('button', name='Connect Wallet').nth(0).click()
        bot.ads.page.get_by_test_id('wallet-icon-backpackeclipse').click()
        backpack_connect_button = bot.ads.page.get_by_test_id('select-hardware-wallet-connect-button')
        bot.backpack.connect(backpack_connect_button)

    random_sleep(5, 7)

    # Проверяем все ли подключилось и логинимся, если нет
    if not bot.ads.page.get_by_role('button', name='Connect Wallet').count() and bot.ads.wait_result('Loading', negative=True):
        # bot.ads.wait_result(cow_element)
        random_sleep()
        if bot.ads.page.get_by_role('button', name='Log in').count():
            for _ in range(3):
                try:
                    with bot.ads.context.expect_page() as page_catcher:
                        bot.ads.page.get_by_role('button', name='Log in').click()
                        # bot.ads.page.locator('canvas').click()

                    approve_page = page_catcher.value
                    approve_page.get_by_text('Approve').nth(1).click()
                    break
                except:
                    logger.warning('Не удалось поймать всплывающее окно')
        random_sleep(1, 3)

    # disable_animations(bot)

    # Делаем три пробных клика. Если появляется табличка с докупкой газа - докупаем
    for _ in range(3):
        try:
            bot.ads.page.evaluate('document.querySelector("canvas").parentElement.click()')
            random_sleep()
            if bot.ads.page.get_by_text('Preload Gas').count():
                bot.backpack.send_tx(bot.ads.page.get_by_role('button', name='Continue'))
                random_sleep(5, 8)
                break
        except:
            pass

    # Отключаем анимацию коровы, чтоб не жрала память
    disable_animations(bot)
    # Считываем количество очков для мониторинга
    score_before = bot.ads.page.locator('number-flow-react').get_attribute('aria-label').replace(',', '')
    if not score_before:
        score_before = 0
    logger.info(f'Счет вначале: {score_before}')
    cliks = random.randint(500, 1000)
    # bot.ads.human_like_clicks(cow_element, cliks)

    override_setTimeout(bot)
    bot.ads.page.unroute('**/*')  # Очищаем предыдущие правила
    bot.ads.page.route('**/*', intercept_requests)

    done_clicks = 0
    double_click_chance = 0.3
    for _ in range(cliks):
        try:
            bot.ads.page.evaluate('document.querySelector("canvas").parentElement.click()')
            done_clicks += 1

            # 🎯 Случайный двойной клик (30% вероятность по умолчанию)
            if random.random() < double_click_chance:
                random_sleep(0.1, 0.2)  # Короткая пауза между двойным кликом
                bot.ads.page.evaluate('document.querySelector("canvas").parentElement.click()')
                done_clicks += 1

            # Случайная задержка перед кликом
            random_sleep(0.1, 0.2)
        except Exception as e:
            print(f'Ошибка при клике: {e}')

    bot.ads.page.unroute('**/*')  # Очищаем правила

    random_sleep(3, 5)
    # Снова считываем очки
    score = bot.ads.page.locator('number-flow-react').get_attribute('aria-label').replace(',', '')
    bot.excel.set_cell('Score', score)
    logger.success(f'Тыканье коровы закончено.\n'
                   f'Совершено кликов: {done_clicks}\n'
                   f'Набрано очков: {score - score_before}\n'
                   f'Очков всего: {score}')