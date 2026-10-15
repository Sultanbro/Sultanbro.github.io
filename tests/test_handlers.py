import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as Obj
from unittest.mock import AsyncMock, Mock
from aiogram.utils.exceptions import TelegramAPIError
from handlers import register_handlers
from shop import Orders


class HandlerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.orders = Orders(Path(temp.name) / 'orders.sqlite3')
        self.bot = AsyncMock()
        self.start, self.buy, self.checkout, self.success = register_handlers(Mock(), self.bot, self.orders, 'demo', Mock())

    def message(self, data='1'):
        return Obj(chat=Obj(id=7, type='private'), from_user=Obj(id=7), web_app_data=Obj(data=data))

    async def test_invalid_webapp_data_never_creates_invoice(self):
        await self.buy(self.message('invalid'))
        self.bot.send_invoice.assert_not_awaited()
        self.bot.send_message.assert_awaited_once()

    async def test_invoice_uses_server_price_and_unique_order(self):
        await self.buy(self.message())
        params = self.bot.send_invoice.call_args.kwargs
        self.assertEqual(params['prices'][0].amount, 1000000)
        self.orders.check(params['payload'], 7, 1000000, 'RUB')

    async def test_checkout_rejects_wrong_amount(self):
        order = self.orders.create(7, '1')
        await self.checkout(Obj(id='query', invoice_payload=order, from_user=Obj(id=7), total_amount=1, currency='RUB'))
        self.assertFalse(self.bot.answer_pre_checkout_query.call_args.kwargs['ok'])

    async def test_checkout_accepts_matching_order(self):
        order = self.orders.create(7, '1')
        await self.checkout(Obj(id='query', invoice_payload=order, from_user=Obj(id=7), total_amount=1000000, currency='RUB'))
        self.assertTrue(self.bot.answer_pre_checkout_query.call_args.kwargs['ok'])

    async def test_duplicate_payment_does_not_repeat_confirmation(self):
        message = self.message()
        message.successful_payment = Obj(invoice_payload=self.orders.create(7, '1'), total_amount=1000000,
                                         currency='RUB', telegram_payment_charge_id='charge')
        await self.success(message)
        await self.success(message)
        self.bot.send_message.assert_awaited_once()

    async def test_failed_invoice_is_cancelled(self):
        self.bot.send_invoice.side_effect = TelegramAPIError('Test failure')
        await self.buy(self.message())
        order = self.bot.send_invoice.call_args.kwargs['payload']
        with self.assertRaises(ValueError):
            self.orders.check(order, 7, 1000000, 'RUB')
