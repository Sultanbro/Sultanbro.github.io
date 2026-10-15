"""Telegram handlers. Bot and storage are injected so tests never contact Telegram."""
from aiogram.types import ContentType, LabeledPrice
from aiogram.utils.exceptions import TelegramAPIError
from shop import CURRENCY, product


def register_handlers(dp, bot, orders, payments_token, keyboard):
    async def start(message):
        await bot.send_message(message.chat.id, 'Откройте демо-каталог и выберите набор.', reply_markup=keyboard)

    async def buy_process(message):
        if message.chat.type != 'private':
            return
        try:
            item = product(message.web_app_data.data)
        except ValueError as error:
            await bot.send_message(message.chat.id, str(error))
            return
        order_id = orders.create(message.from_user.id, message.web_app_data.data)
        try:
            await bot.send_invoice(message.chat.id, title=item['title'], description='Демонстрационный заказ',
                                   provider_token=payments_token, currency=CURRENCY,
                                   prices=[LabeledPrice(label=item['title'], amount=item['amount'])],
                                   start_parameter='demo-order', payload=order_id)
        except TelegramAPIError:
            orders.cancel(order_id)
            await bot.send_message(message.chat.id, 'Не удалось создать счёт. Попробуйте снова.')

    async def checkout_process(query):
        try:
            orders.check(query.invoice_payload, query.from_user.id, query.total_amount, query.currency)
        except ValueError as error:
            await bot.answer_pre_checkout_query(query.id, ok=False, error_message=str(error))
            return
        await bot.answer_pre_checkout_query(query.id, ok=True)

    async def successful_payment(message):
        payment = message.successful_payment
        try:
            fresh = orders.paid(payment.invoice_payload, message.from_user.id, payment.total_amount,
                                payment.currency, payment.telegram_payment_charge_id)
        except ValueError:
            await bot.send_message(message.chat.id, 'Платёж требует ручной проверки заказа.')
            return
        if fresh:
            await bot.send_message(message.chat.id, 'Оплата демо-заказа зарегистрирована.')

    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(buy_process, content_types=ContentType.WEB_APP_DATA)
    dp.register_pre_checkout_query_handler(checkout_process, lambda query: True)
    dp.register_message_handler(successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT)
    return start, buy_process, checkout_process, successful_payment
