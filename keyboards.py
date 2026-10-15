from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo


def make_keyboard(url):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Открыть каталог', web_app=WebAppInfo(url=url))]],
                               resize_keyboard=True)
