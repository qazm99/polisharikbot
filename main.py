from settings import API_TOKEN, bd_link


import asyncio
import logging
import datetime
import random
import sqlite3 as sl

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command



def gen_randoom():
    rand_number = random.randint(1, 6)
    return rand_number

def connect_db():
    db_connect = sl.connect(bd_link)

    table_exist = db_connect.execute("select count(*) from sqlite_master where type='table' and name='gen_nums'")
    for table_exist_num in table_exist:
        if table_exist_num[0] == 0:
            with db_connect:
                db_connect.execute("""
                    CREATE TABLE gen_nums (
                        user_id INTEGER,
                        gen_num INTEGER,
                        date_gen TEXT
                    );
                """)
    return db_connect

def return_cur_num_user(cur_user_id: int, db_link):
    with db_link:
        cursor = db_link.cursor()
        cursor.execute(f"SELECT gen_num FROM gen_nums WHERE date_gen = date('now', '+3 hours') AND user_id = {cur_user_id}")
        cur_num_user = cursor.fetchone()

    if cur_num_user:
        return cur_num_user[0]
    else:
        return cur_num_user

def set_num_bd(cur_user_id: int, db_link):
    cur_num = gen_randoom()
    with db_link:
        cursor = db_link.cursor()
        cursor.execute(f"INSERT INTO Gen_nums (user_id, gen_num, date_gen) VALUES ({cur_user_id}, {cur_num}, date('now', '+3 hours'));")
        cur_num_user = cursor.fetchone()

    return cur_num

router = Router()

@router.message(Command("rnd"))
async def start_handler(msg: Message):
    print(f"user id:{msg.from_user.id}")
    db_users = connect_db()
    cur_num_user = return_cur_num_user(msg.from_user.id, db_users)
    if not cur_num_user:
        cur_num_user = set_num_bd(msg.from_user.id, db_users)

    print(cur_num_user)
    cur_day = datetime.datetime.now().weekday()
    if cur_day in [0, 2, 4, 6]:
        cur_len = cur_num_user*2 + 1
        await msg.answer(f"Для вас {msg.from_user.full_name} @{msg.from_user.username} лототрон выдал {cur_num_user}, но не расслабляйтесь - бежать вам {cur_len} км.")
    else:
        await msg.answer(f"Уважаемый и прекрасный человек {msg.from_user.full_name} @{msg.from_user.username} почитайте правила, сегодня кубики не кидаем. Но если вам просто скучно - держите {cur_num_user}")

@router.message(Command("rndtest"))
async def start_handler(msg: Message):
    print(f"user id:{msg.from_user.id}")
    cur_num_user = gen_randoom()
    print(cur_num_user)
    await msg.answer(f"Для вас {msg.from_user.full_name} @{msg.from_user.username} лототрон выдал {cur_num_user}")

async def main():
    bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates= dp.resolve_used_update_types())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())