from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

async def osnova():
    btn1 = KeyboardButton('👷‍♂️Рефералы')
    btn2 = KeyboardButton('🔨Премиум доступ')

    keyboard = ReplyKeyboardMarkup().add(btn1, btn2)

    return keyboard

async def ref():
    btn1 = InlineKeyboardButton('Получить ссылку', callback_data='give')

    keyboard = InlineKeyboardMarkup().add(btn1)

    return keyboard