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
        Factor = 1       # Сколько штук парсится за раз (За проходку более 100 вроде не парсит)
        Filter = 'hentai'
        c = 0

        data = '{"query":" query SubredditQuery( $url: String! $filter: SubredditPostFilter $iterator: String ) { getSubreddit(url: $url) { children( limit: 999999 iterator: $iterator filter: $filter disabledHosts: null ) { iterator items { __typename url title subredditTitle subredditUrl redditPath isNsfw albumUrl isFavorite mediaSources { url width height isOptimized } } } } } ","variables":{"url":"/r/'+str(Filter)+'","limit": '+str(Factor)+',"filter":"PICTURE","hostsDown":null},"authorization":null}'
        resp = r.post('https://api.scrolller.com/api/v2/graphql', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        data_images = json.loads(resp.text)
        for item in data_images['data']['getSubreddit']['children']['items']:
            url = item['mediaSources'][len(item['mediaSources'])-1]['url']
            print(url)
            c += 1
            if c == 1:
                break
        await bot.send_photo(-1001891127901, photo=url,  caption = '[🔞Самые сочные фулы🔞](https://t.me/benzporn_robot?start=channel)')
        await bot.send_video(msg.chat.id, video = '')
        await msg.answer('Успешно!')
    else:
        pass

@dp.callback_query_handler(lambda c: c.data == 'give')
async def next(c: types.CallbackQuery):
    await bot.answer_callback_query(c.id)

    await c.message.delete()
    if db.profile(msg)[0] < 5:
        await c.message.answer('У вас не достаточно рефералов!')
    else:
        await c.message.answer('Поздравляю, теперь у вас есть доступ!')
        chat_id = -1001506130892
        expire_date = datetime.now() + timedelta(days=1)
        link = await bot.create_chat_invite_link(chat_id, expire_date.timestamp, 1)

        await c.message.answer(link.invite_link)

@dp.message_handler(content_types=['text'])
async def ref(msg: types.Message):
    if msg.text == '👷‍♂️Рефералы':
        markup = await keyboard.ref()

        info = db.profile(msg)

        await msg.answer(f'''
Ваша реф ссылка `https://t.me/benzporn_robot?start={msg.chat.id}`

Всего рефералов {info[0]}
При 5 рефералов вы получаете бесплатный доступ!
''', reply_markup = markup)
    if msg.text == '🔨Премиум доступ':
        async with QiwiWrapper(secret_p2p = qiwi) as w:
            bill = await w.create_p2p_bill(
            amount = 99,
            comment = f'Оплата доступа на сумму {msg.text}\nКод - {random.randint(100, 999)}',
            life_time = datetime.now() + timedelta(minutes = 10))

            check = await w.check_p2p_bill_status(bill_id = bill.id)
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton('Оплатить 99Р', url = bill.pay_url))

            await msg.answer(f'Выставлен счет, у вас есть 10 минут на его оплату!', reply_markup=markup)
            while True:

                if check == "PAID":
                    chat_id = -1001506130892
                    expire_date = datetime.now() + timedelta(days=1)
                    link = await bot.create_chat_invite_link(chat_id, expire_date.timestamp, 1)

                    await msg.reply(link.invite_link)
                    await msg.answer('Поздравляю вас с покупкой премиума!')
                    break
                            
                if check == 'EXPIRED':
                    await msg.answer('Вы не успели(')
                    break


async def scheduled1():
    Factor = 1       # Сколько штук парсится за раз (За проходку более 100 вроде не парсит)
    Filter = 'hentai'
    c = 0

    data = '{"query":" query SubredditQuery( $url: String! $filter: SubredditPostFilter $iterator: String ) { getSubreddit(url: $url) { children( limit: 999999 iterator: $iterator filter: $filter disabledHosts: null ) { iterator items { __typename url title subredditTitle subredditUrl redditPath isNsfw albumUrl isFavorite mediaSources { url width height isOptimized } } } } } ","variables":{"url":"/r/'+str(Filter)+'","limit": '+str(Factor)+',"filter":"PICTURE","hostsDown":null},"authorization":null}'
    resp = r.post('https://api.scrolller.com/api/v2/graphql', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    data_images = json.loads(resp.text)
    for item in data_images['data']['getSubreddit']['children']['items']:
        url = item['mediaSources'][len(item['mediaSources'])-1]['url']
        print(url)
        c += 1
        if c == 1:
            break
    await bot.send_photo(-1001891127901, photo=url,  caption = '[🔞Самые сочные фулы🔞](https://t.me/benzporn_robot?start=channel)')


async def scheduleds():
    Factor = 1       # Сколько штук парсится за раз (За проходку более 100 вроде не парсит)
    Filter = 'nsfw'
    c = 0

    data = '{"query":" query SubredditQuery( $url: String! $filter: SubredditPostFilter $iterator: String ) { getSubreddit(url: $url) { children( limit: 999999 iterator: $iterator filter: $filter disabledHosts: null ) { iterator items { __typename url title subredditTitle subredditUrl redditPath isNsfw albumUrl isFavorite mediaSources { url width height isOptimized } } } } } ","variables":{"url":"/r/'+str(Filter)+'","limit": '+str(Factor)+',"filter":"PICTURE","hostsDown":null},"authorization":null}'
    resp = r.post('https://api.scrolller.com/api/v2/graphql', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    data_images = json.loads(resp.text)
    for item in data_images['data']['getSubreddit']['children']['items']:
        url = item['mediaSources'][len(item['mediaSources'])-1]['url']
        c += 1
        if c == 1:
            break
    await bot.send_photo(-1001506130892, photo=url,  caption = '🔞👀')
    print('did')

scheduler.add_job(scheduled1, "interval", seconds=1800)
scheduler.add_job(scheduleds, 'interval', seconds=3600)
scheduler.start()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
