"""Server-owned catalogue and persistent demo orders; no Telegram dependency."""
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

CATALOG = {str(i): {"title": f"Демо-набор {i}", "amount": i * 1000000} for i in range(1, 7)}
CURRENCY = "RUB"


def product(item_id):
    if not isinstance(item_id, str) or item_id not in CATALOG:
        raise ValueError("Выберите товар из каталога.")
    return CATALOG[item_id]


class Orders:
    def __init__(self, path="data/orders.sqlite3"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = str(path)
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, item_id TEXT NOT NULL,
                amount INTEGER NOT NULL, currency TEXT NOT NULL, created REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending', charge_id TEXT UNIQUE)""")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def create(self, user_id, item_id):
        item = product(item_id)
        order_id = uuid.uuid4().hex
        with self.connect() as db:
            db.execute("INSERT INTO orders (id,user_id,item_id,amount,currency,created) VALUES (?,?,?,?,?,?)",
                       (order_id, user_id, item_id, item["amount"], CURRENCY, time.time()))
        return order_id

    def _matching(self, db, order_id, user_id, amount, currency):
        row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
        if row is None or row["user_id"] != user_id or row["amount"] != amount or row["currency"] != currency:
            raise ValueError("Данные заказа не совпадают. Создайте новый счёт.")
        return row

    def check(self, order_id, user_id, amount, currency):
        with self.connect() as db:
            row = self._matching(db, order_id, user_id, amount, currency)
            if row["status"] != "pending" or time.time() - row["created"] > 1800:
                raise ValueError("Счёт уже обработан или истёк. Создайте новый счёт.")

    def paid(self, order_id, user_id, amount, currency, charge_id):
        if not charge_id:
            raise ValueError("Отсутствует идентификатор платежа.")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._matching(db, order_id, user_id, amount, currency)
            if row["status"] == "paid":
                if row["charge_id"] != charge_id:
                    raise ValueError("Заказ уже оплачен другим платежом.")
                return False
            if row["status"] != "pending":
                raise ValueError("Счёт отменён.")
            try:
                db.execute("UPDATE orders SET status='paid', charge_id=? WHERE id=?", (charge_id, order_id))
            except sqlite3.IntegrityError as exc:
                raise ValueError("Платёж уже связан с другим заказом.") from exc
            return True

    def cancel(self, order_id):
        with self.connect() as db:
            db.execute("UPDATE orders SET status='cancelled' WHERE id=? AND status='pending'", (order_id,))
