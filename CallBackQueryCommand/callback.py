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

from CONFIG.confident import API_TOKEN, CHAT_ID

async def admin_1(callback_query: CallbackQuery, state: FSMContext, Form):
    await callback_query.answer()
    await callback_query.message.answer('Ок, введи название темы')
    await state.set_state(Form.create_theam)


async def admin_2(callback_query: CallbackQuery, state: FSMContext, Form):
    await callback_query.answer()
    await callback_query.message.answer('Отлично, отправь задания в словря  с ключами (url, type, chat_id, money)')
    await state.set_state(Form.create_bonus)


async def admin_3(callback_query: CallbackQuery, state: FSMContext, Form):
    await callback_query.answer()
    await callback_query.message.answer('Введи url')
    await state.set_state(Form.delete_bonus)

    
async def check_profile(callback_query: CallbackQuery, state: FSMContext, res_0):
    res = await res_0.get_param_user()
    info, data = res
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(f'''-------\U0001F4CA Ваши текущие данные\U0001F4CA--------
        \n  \U0001F4B0 Сумма монет: {data['count_money']} \U0001F4B0
        \n  \U0001F5F3 Ваши голоса: {data['your_vote']} \U0001F5F3
        \n  \U0001F4CB Открытые вами опросы: {data['your_open_poll']} \U0001F4CB
        \n  \U00002705 Закрытые вами опросы: {data['your_close_poll']} \U00002705
        \n  \U0001F4C5 Дата регистрации: {info['date_register']} \U0001F4C5''')