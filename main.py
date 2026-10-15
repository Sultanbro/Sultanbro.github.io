from aiogram import Bot, Dispatcher, executor
from config import BOT_TOKEN, PAYMENTS_TOKEN, WEBAPP_URL, ORDERS_DB
from handlers import register_handlers
from keyboards import make_keyboard
from shop import Orders


def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(bot)
    register_handlers(dp, bot, Orders(ORDERS_DB), PAYMENTS_TOKEN, make_keyboard(WEBAPP_URL))
    executor.start_polling(dp, skip_updates=False)


if __name__ == '__main__':
    main()
