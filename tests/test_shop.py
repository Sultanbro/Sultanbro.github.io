import tempfile
import time
import unittest
from pathlib import Path
from shop import Orders, product


class OrderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'orders.sqlite3'
        self.orders = Orders(self.path)
        self.order = self.orders.create(7, '1')

    def test_price_is_selected_on_server(self):
        self.orders.check(self.order, 7, 1000000, 'RUB')
        self.assertEqual(product('6')['amount'], 6000000)

    def test_unknown_product_is_rejected(self):
        for item in ('', '0', '7', '{"price":1}', None, 1):
            with self.subTest(item=item), self.assertRaises(ValueError):
                product(item)

    def test_wrong_owner_amount_currency_or_order_are_rejected(self):
        for args in [(self.order, 8, 1000000, 'RUB'), (self.order, 7, 1, 'RUB'),
                     (self.order, 7, 1000000, 'USD'), ('unknown', 7, 1000000, 'RUB')]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.orders.check(*args)

    def test_expired_order_is_rejected_at_checkout(self):
        with self.orders.connect() as db:
            db.execute('UPDATE orders SET created=?', (time.time() - 1900,))
        with self.assertRaises(ValueError):
            self.orders.check(self.order, 7, 1000000, 'RUB')

    def test_cancelled_invoice_cannot_be_paid(self):
        self.orders.cancel(self.order)
        with self.assertRaises(ValueError):
            self.orders.check(self.order, 7, 1000000, 'RUB')
        with self.assertRaises(ValueError):
            self.orders.paid(self.order, 7, 1000000, 'RUB', 'charge-1')

    def test_repeated_success_is_idempotent_and_survives_restart(self):
        self.assertTrue(self.orders.paid(self.order, 7, 1000000, 'RUB', 'charge-1'))
        reopened = Orders(self.path)
        self.assertFalse(reopened.paid(self.order, 7, 1000000, 'RUB', 'charge-1'))
        with self.assertRaises(ValueError):
            reopened.check(self.order, 7, 1000000, 'RUB')

    def test_success_event_validates_owner_and_amount(self):
        with self.assertRaises(ValueError):
            self.orders.paid(self.order, 8, 1000000, 'RUB', 'charge-1')
        with self.assertRaises(ValueError):
            self.orders.paid(self.order, 7, 1, 'RUB', 'charge-1')

    def test_charge_cannot_be_reused_for_another_order(self):
        second = self.orders.create(7, '1')
        self.orders.paid(self.order, 7, 1000000, 'RUB', 'charge-1')
        with self.assertRaises(ValueError):
            self.orders.paid(second, 7, 1000000, 'RUB', 'charge-1')

    def test_different_charge_cannot_overwrite_paid_order(self):
        self.orders.paid(self.order, 7, 1000000, 'RUB', 'charge-1')
        with self.assertRaises(ValueError):
            self.orders.paid(self.order, 7, 1000000, 'RUB', 'charge-2')

    def test_empty_charge_is_rejected(self):
        with self.assertRaises(ValueError):
            self.orders.paid(self.order, 7, 1000000, 'RUB', '')
