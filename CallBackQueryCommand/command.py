import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, PollAnswer
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from DB.db_class import *

from CONFIG.data_class import CallBackMarkup
from CONFIG.config import DataCallBack
from CONFIG.formating import *


async def admin(message: Message, state: FSMContext):
    async with AdminWork(message.from_user.id) as admin:
        if await admin.check_admin():     
            keyboard = CallBackMarkup(DataCallBack.ADMIN_FUNC, 1)
            await message.answer("Привет господин админ, выбери действие", reply_markup = await keyboard.get_markup())
        else:
            await message.answer(f'{message.from_user.id}')


async def start(message: Message, state: FSMContext):
    async with ConnectUserToBD(message.from_user.id) as obj_bd_user:
        if not await obj_bd_user.check_user():
            await message.answer('Поздравляю, это твой первый раз в нашем боте!')
            user_create = DbCreateUser(message.from_user.id, message.from_user.language_code)
            await user_create()
            await user_create.a()
            await user_create.close()
        keyboard = CallBackMarkup(DataCallBack.GLOBAL_DCITER, 3)
        await state.update_data(con_user=obj_bd_user)
        await message.answer('Привет! 👋 Рад тебя видеть! Давай выберем, что делать дальше. Выбери одно из действий:', reply_markup = await keyboard.get_markup())


async def get_data(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(data)
    await message.answer(f'{await state.get_data()}')


async def help(message: Message, state: FSMContext):
    await message.answer('У тебя возникли вопросы? Отправь их на @Regqwe')


async def news(message: Message, state: FSMContext):
    keyboard = CallBackMarkup({'Присоединиться к каналу': 'https://t.me/poll_reg'}, row=1, additional_data='url')
    await message.answer('''🔔 Следите за новостями и обновлениями нашего бота!
        👉 Чтобы быть в курсе всех новинок и получать важные обновления, перейдите по ссылке ниже:
        💬 Здесь вы найдете свежие новости, улучшения и важные анонсы! Не пропустите!''', reply_markup = await keyboard.get_markup())


async def tasks(message: Message, state: FSMContext):
    async with ConnectUserToBD(message.from_user.id) as con:
        res = await con.get_chanels()
        if not res:
            await message.answer('Пока нет заданий, возвращайтесь позже')
            return
        dicters_p = {f'Получить {e['money']} монет': e['url'] for e in res}
        keyboard = CallBackMarkup(dicters_p, row=3, additional_data='url')
        await keyboard.other_param_add('check_bonus', 'Проверить')
        await message.answer('Отлично подпишись на каналы и получи бонусы', reply_markup= await keyboard.get_markup())
        await state.update_data(bonus=res)
        

async def cooperation(message: Message):
    await message.answer('Пишите @regqwe')


