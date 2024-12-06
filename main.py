import asyncio
import flask

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from DB.db_class import *

from CONFIG.data_class import CallBackMarkup
from CONFIG.config import DataCallBack
from CONFIG.formating import *

from time import API_TOKEN

bot = Bot(token=API_TOKEN)

dp = Dispatcher()


class Form(StatesGroup):
    create_theam = State()
    create_pull = State()
    create_pull_step_2 = State()
    create_pull_step_3 = State()


@dp.message(Command('start'))
async def get_info(message: Message, state: FSMContext):
    async with ConnectUserToBD(message.from_user.id) as obj_bd_user:
        if not await obj_bd_user.check_user():
            await message.answer('Поздравляю, это твой первый раз в нашем боте!')
            user_create = DbCreateUser(message.from_user.id, message.from_user.language_code)
            await user_create()
            await user_create.a()
            await user_create.close()
        keyboard = CallBackMarkup(DataCallBack.GLOBAL_DCITER, 3)
        await state.update_data(con_user=obj_bd_user)
        await message.answer('Привет, я хочу помочь тебе выбери действие', reply_markup = await keyboard.get_markup())


@dp.message(Command('admin'))
async def open_admin_f(message: Message):
    async with AdminWork(message.from_user.id) as admin:
        if await admin.check_admin():     
            keyboard = CallBackMarkup(DataCallBack.ADMIN_FUNC, 1)
            await message.answer("Привет господин админ, выбери действие", reply_markup = await keyboard.get_markup())
        else:
            await message.answer(f'{message.from_user.id}')
        # Обработка callback запроса

@dp.message(Command('get_data'))
async def get_data_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(data)
    await message.answer(f'{await state.get_data()}')

@dp.callback_query()
async def handle_callback(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if data:
        if callback_query.data[:6] == 'topic_':
            await callback_query.answer()
            theam = callback_query.data[6:]
            keyboard = CallBackMarkup({'❌': 'end_pull', '➡️': 'continue'}, row=2)

            new_con_user = ConnectUserToBD(data.get('con_user').id_user)
            await new_con_user.connect()
            await state.update_data(short_trem_con=new_con_user)
            await state.update_data(theam_find=theam)
            await state.update_data(timer=datetime.datetime.now())

            await callback_query.message.answer('отллично', reply_markup=await keyboard.get_markup())
        elif callback_query.data == 'continue':
            if not data.get('short_tream_con'):
                k = CallBackMarkup({'🔄': '1.1', '❌': 'end_pull'}, row=2)
                await callback_query.answer('Произошел сбой', reply_markup= await k.get_markup())
                return None
            

            
        elif callback_query.data == 'end_pull':
            pass
        
        async with data.get('con_user') as res_0:
            if callback_query.data == "1":
                res = await res_0.get_param_user()
                info, data = res
                await callback_query.message.delete()
                await callback_query.answer()
                await callback_query.message.answer(f'''-------\U0001F4CA Ваши текущие данные\U0001F4CA--------
                    \n  \U0001F4B0 Сумма монет: {data['count_money']} \U0001F4B0
                    \n  \U0001F5F3 Ваши голоса: {data['your_vote']} \U0001F5F3
                    \n  \U0001F4CB Открытые вами опросы: {data['your_open_pull']} \U0001F4CB
                    \n  \U00002705 Закрытые вами опросы: {data['your_close_pull']} \U00002705
                    \n  \U0001F4C5 Дата регистрации: {info['date_register']} \U0001F4C5''')

            elif callback_query.data == "1.1":
                res = {e: f'topic_{e}'  for e in (map(lambda x: x['topic_name'], await res_0.get_theam()))}
                keyboard = CallBackMarkup(res, 3)
                await callback_query.message.delete()
                await callback_query.answer()
                await callback_query.message.answer(f"Выберите тему:", reply_markup= await keyboard.get_markup())

            elif callback_query.data == '1.2':
                await callback_query.answer()
                await callback_query.message.answer(f'Введи описания запроса')
                await state.set_state(Form.create_pull)
            elif callback_query.data == '1.2.Yes':
                keyboard = CallBackMarkup({'Оплатить': 'https://pay.cryptocloud.plus/pos/Pha6eECebKkcPcDY'}, row=1, additional_data='url')
                await callback_query.answer('Отлично, почти все готово, осталось оплатить заказ', reply_markup= await keyboard.get_markup())
                await callback_query.message.answer('Хорошо, запрос должен пройти модерацию,по вопросам пишите @Regqwe')
                dt  = await state.get_data()
                e = await res_0.create_pull(await get_dicter(dt))
                
            elif callback_query.data == '1.2.No':
                await state.clear()
                await state.update_data(con_user=res_0)

            elif callback_query.data[:8] == 'p_topic_':
                topic = callback_query.data[8:]
                await callback_query.answer()
                await callback_query.message.reply('Отлично, отправь url если нужно, если не нужно, то оптравь none')
                await state.update_data(topics=topic)
                await state.set_state(Form.create_pull_step_3)

            elif callback_query.data == 'end.1':
                await callback_query.answer()
                await callback_query.message.reply('Отличнно, теперь отправь опрос')
                await state.set_state(Form.create_pull)

            elif callback_query.data == 'admin.1':
                await callback_query.answer()
                await callback_query.message.answer('Ок, введи название темы')
                await state.set_state(Form.create_theam)
    else:
        await callback_query.message.answer("Кажется, что произошел сбой, попробуйте /start")


@dp.message(Form.create_theam)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    async with  AdminWork(message.from_user.id) as admin:
        if await admin.check_admin():
            state_a = await admin.add_topic(message.text)
            if not state_a:
                await message.answer(f"Тема добавлена успешна")
            else:
                await message.answer(f"ошибка {state_a}")


@dp.message(Form.create_pull)
async def step_1_create_pull(message: Message, state: FSMContext) -> None:
    poll = message.poll
    data = await state.get_data() 
    async with data.get('con_user') as con_user:
        if poll:
            dicter = {
                'question': poll.question,
                'options': list(map(lambda x: x.text, poll.options)),
                'anonymous': poll.is_anonymous,
                'multiple': poll.allows_multiple_answers,
            }
            res = {e: f'p_topic_{e}'  for e in (map(lambda x: x['topic_name'], await con_user.get_theam()))}
            keyboard = CallBackMarkup(res, 3)
            await message.reply('Отлично, теперь выбери тему к которой это относиться, если нет подходящей пиши @Regqwe',  reply_markup = await keyboard.get_markup())
            await state.update_data(data_pull=dicter)
            # await state.set_state(Form.create_pull_step_2)
        else:
            await message.answer('Это не опрос, попробуй заново')


@dp.message(Form.create_pull_step_3)
async def step_3_create_pull(message: Message, state: FSMContext) -> None:
    text = message.text
    if not text == 'none'.lower():
        await state.update_data(url=message.text)
        try:
            kb = CallBackMarkup({'Test URl': message.text}, 1, additional_data='url')
            await message.answer(text='Пример ссылки', reply_markup= await kb.get_markup())
        except Exception as e:
            await message.answer(f'Произошла ошибка, попробуйте другой url {e}')
            return None
    else:
        await state.update_data(url=None)
    await state.set_state(Form.create_pull_step_2)
    await message.answer('Хорошо, отправь кол-во голосов, до которого будут проводиться голоса максимум 10000')


@dp.message(Form.create_pull_step_2)
async def step_2_create_pull(message: Message, state: FSMContext) -> None:
    count = message.text
    try:
        count = int(count)
        if type(count) is int and count < 10000:
            await state.update_data(max_vote=count)
            data = await state.get_data()
            data_p = data.get('data_pull')
            con_user = data.get('con_user')
            if data.get('url'):
                keyboard_to = CallBackMarkup({'URL': data['url']}, 1, additional_data='url') 
                await message.answer_poll(
                    question=data_p['question'],
                    options=data_p['options'],
                    is_anonymous=data_p['anonymous'],
                    allows_multiple_answers=data_p['multiple'], reply_markup= await keyboard_to.get_markup()
            )
            else:
                await message.answer_poll(
                    question=data_p['question'],
                    options=data_p['options'],
                    is_anonymous=data_p['anonymous'],
                    allows_multiple_answers=data_p['multiple']),
            keyboard = CallBackMarkup({'Принять': '1.2.Yes', 'Отклонить': '1.2.No'}, 2)    
            await message.answer(f'отлично, вот как будет выглядить опрос у других', reply_markup= await keyboard.get_markup())


        else:
            raise ValueError
    except ValueError as e:
        await message.answer(f'Введи правильное количество {count}')




async def main():
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == '__main__':
    asyncio.run(main()) 