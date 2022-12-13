from aiogram import  Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import cfg, db, keyboard, json
import logging, asyncio
import requests as r
import random

from cfg import qiwi
from glQiwiApi import QiwiWallet, QiwiWrapper

from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

admin = cfg.admin

logging.basicConfig(level = logging.INFO)

bot = Bot(token = cfg.TOKEN, parse_mode='Markdown')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    markup = await keyboard.osnova()

    unique_code = extract_unique_code(msg.text)
    print(db.check_ref(msg))
    if db.check_ref(msg) is None:
        if unique_code:    
            db.add_ref(msg, unique_code)
            await msg.reply('Привет❕ Тут ты можешь купить ИЛИ ЗАБРАТЬ ДОСТУП ЗА 5 РЕФЕРАЛОВ', reply_markup=markup)
        else:
            db.add_ref(msg, None)
            await msg.reply('Привет❕ Тут ты можешь купить ИЛИ ЗАБРАТЬ ДОСТУП ЗА 5 РЕФЕРАЛОВ', reply_markup=markup)
    else:
        await msg.reply('Привет❕ Тут ты можешь купить ИЛИ ЗАБРАТЬ ДОСТУП ЗА 5 РЕФЕРАЛОВ', reply_markup=markup)

@dp.message_handler(commands=['new'])
async def scheduled(msg: types.Message):
    if msg.chat.id == int(admin):
        await scheduled1()
    else:
        pass

@dp.callback_query_handler(lambda c: c.data == 'give')
async def back(c: types.CallbackQuery):
    await bot.answer_callback_query(c.id)
    await c.message.delete()

    info = db.profile(c.message)
        
    if info[0] < 5:
        await c.message.answer('У вас недостаточно рефералов!')
    else:
        chat_id = -1001506130892
        expire_date = datetime.now() + timedelta(days=1)
         
        link = await bot.create_chat_invite_link(chat_id, expire_date.timestamp, 1)

        await c.message.answer(link.invite_link + '\n\nПоздравляю, теперь у вас есть премиум подписка!')

async def buy(msg):
    async with QiwiWrapper(secret_p2p = qiwi) as w:
        bill = await w.create_p2p_bill(
            amount = 49,
            comment = f'Оплата доступа на сумму 49₽\nКод - {random.randint(100, 999)}',
            life_time = datetime.now() + timedelta(minutes = 10))

        btn1 = InlineKeyboardButton('Оплатить 49₽', url = bill.pay_url)
        markup = InlineKeyboardMarkup().add(btn1)

        await msg.answer(f'Выставлен счет, у вас есть 10 минут на его оплату!', reply_markup=markup)
        seconds = 600
        repeats = [1 for i in range(0, seconds)]
        for i in repeats:
            check = await w.check_p2p_bill_status(bill_id = bill.id)
            if check == "PAID":
                chat_id = -1001506130892
                expire_date = datetime.now() + timedelta(days=1)
                link = await bot.create_chat_invite_link(chat_id, expire_date.timestamp, 1)

                await msg.reply(link.invite_link)
                await msg.answer('Поздравляю вас с покупкой премиума!')
                break
                            
            if check == 'EXPIRED':
                await bot.edit_message_text(msg, 'Вы не успели((')
                break
            
            await asyncio.sleep(10)



@dp.message_handler(content_types=['text'])
async def ref(msg: types.Message):
    info = db.profile(msg) 

    if msg.text == '👷‍♂️Рефералы':
        markup = await keyboard.ref()
   
        await msg.answer(f'''
Ваша реф ссылка `https://t.me/benzporn_robot?start={msg.chat.id}`

Всего рефералов {info[0]}
При 5 рефералов вы получаете бесплатный доступ!
    ''', reply_markup = markup)     
    if msg.text == '🔨Премиум доступ':
        await buy(msg)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
