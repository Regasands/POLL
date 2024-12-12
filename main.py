import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, PollAnswer
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from DB.db_class import *

from CONFIG.data_class import CallBackMarkup
from CONFIG.config import DataCallBack
from CONFIG.formating import *

from CONFIG.confident import API_TOKEN, CHAT_ID

from CallBackQueryCommand import command, callback
bot = Bot(token=API_TOKEN)

dp = Dispatcher()


class Form(StatesGroup):
    create_theam = State()
    create_poll = State()
    create_poll_step_2 = State()
    create_poll_step_3 = State()

    create_bonus = State()
    delete_bonus = State()
    


@dp.message(Command('start'))
async def get_info(message: Message, state: FSMContext):
    await command.start(message, state)


@dp.message(Command('admin'))
async def open_admin_f(message: Message, state: FSMContext):
    await command.admin(message, state)


@dp.message(Command('get_data'))
async def get_data_state(message: Message, state: FSMContext):
    await command.get_data_state(message, state)


@dp.message(Command('news'))
async def get_newss(message: Message, state: FSMContext):
    await command.news(message, state)


@dp.message(Command('help'))
async def get_info_help(message: Message, state: FSMContext):
    await command.help(message, state)

@dp.message(Command('tasks'))
async def get_tasks_help(message: Message, state: FSMContext):
    await command.tasks(message, state)
# @dp.message(Command('help'))
# async def get_info_help(message: Message, state: FSMContext):
#     await command.help(message, state)



# @dp.message(Command('help'))
# async def get_info_help(message: Message, state: FSMContext):
#     await command.help(message, state)

@dp.callback_query()
async def handle_callback(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    Con = data.get('con_user')
    if not Con:
        await callback_query.message.answer("Кажется, что произошел сбой, попробуйте /start")
        return
    async with Con as res_0:
        if callback_query.data[:6] == 'topic_':
            m_p = data.get('poll')
            s = data.get('consumable_poll')
            theam = callback_query.data[6:]

            try:
                await bot.stop_poll(chat_id=m_p[0].chat.id, message_id=m_p[0].message_id)
            except Exception as e:
                pass

            res = await res_0.get_poll(theam, additional_param=s)
            await state.update_data(consumable_poll= s + [res['id_p']]) if res else await state.update_data(consumable_poll=[])

            if not res:
                keyboard = CallBackMarkup({'Выбрать другую тему': '1.1'}, row=1)
                await state.update_data(consumable_poll=[])
                await callback_query.message.answer('На эту тему опросы для тебя закончились, попробуй  заново или другую тему', reply_markup=await keyboard.get_markup())
                return
                
            options = await format_json_f(res['variants'])

            keyboard = CallBackMarkup({'❌': 'end_poll', '➡️': f'topic_{theam}'}, row=2)
            message_poll = await callback_query.message.answer_poll(question=res['description'],
                                options=list(options.keys()),
                                allows_multiple_answers=res['multiple_choice'],
                                is_anonymous=False,  reply_markup=await keyboard.get_markup())

            await state.update_data(poll=[message_poll, options, res, keyboard]) 
            await state.update_data(theam_find=theam)

            await callback_query.answer()

        elif callback_query.data == 'end_poll':
            await callback_query.answer()
            keyboard = CallBackMarkup(DataCallBack.GLOBAL_DCITER, 3)
            await state.clear()
            await state.update_data(con_user=res_0)
            await callback_query.message.answer('Ты верунлся в основное меню',  reply_markup = await keyboard.get_markup())

        elif callback_query.data == "1":
            await callback.check_profile(callback_query, state, res_0)

        elif callback_query.data == "1.1":
            res = {e: f'topic_{e}'  for e in (map(lambda x: x['topic_name'], await res_0.get_theam()))}
            print(res)
            keyboard = CallBackMarkup(res, 3)
            await callback_query.message.delete()
            await callback_query.answer()
            await callback_query.message.answer(f"Выберите тему:", reply_markup= await keyboard.get_markup())

        elif callback_query.data == '1.2':
            await callback_query.answer()
            await callback_query.message.answer(f'Введи описания запроса')
            await state.set_state(Form.create_poll)

        elif callback_query.data == '1.2.Yes':
            keyboard = CallBackMarkup({'Поддержать автора': 'https://pay.cryptocloud.plus/pos/Pha6eECebKkcPcDY'}, row=1, additional_data='url')
            await callback_query.answer('Отлично, пока бот бесплатный, пользуйтесь)', reply_markup= await keyboard.get_markup())
            await callback_query.message.answer('Хорошо, запрос должен пройти модерацию,по вопросам пишите @Regqwe')
            dt  = await state.get_data()
            e = await res_0.create_poll(await get_dicter(dt))
            await callback_query.message.delete()
            await state.clear()
            await state.update_data(con_user=res_0)

        elif callback_query.data == '1.2.No':
            await state.clear()
            await state.update_data(con_user=res_0)

        elif callback_query.data[:8] == 'p_topic_':
            topic = callback_query.data[8:]
            await callback_query.answer()
            await callback_query.message.reply('Отлично, отправь url если нужно, если не нужно, то оптравь none')
            await state.update_data(topics=topic)
            await state.set_state(Form.create_poll_step_3)

        elif callback_query.data == 'end.1':
            await callback_query.answer()
            await callback_query.message.reply('Отличнно, теперь отправь опрос')
            await state.set_state(Form.create_poll)

        elif callback_query.data == 'admin.1':
            await callback.admin_1(callback_query, state, Form)

        elif callback_query.data == 'admin.2':
            await callback.admin_2(callback_query, state, Form)

        elif callback_query.data == 'admin.3':
            await callback.admin_3(callback_query, state, Form)

        elif  callback_query.data == 'check_your_poll':

            res = await res_0.get_your_polls()
            if not res:
                await callback_query.data('У тебя еще нет запросов, создай их!')
                return
            dicter = {f"{record['description'][:7]}..." if len(record['description']) > 7 else f"{record['description'][:7]}": f"id_p{record['id_p']}" for record in res}
            dicters_p = {f"{record['id_p']}": record for record in res}
            keyboard = CallBackMarkup(dicter, row=4)
            await callback_query.message.answer('Список твоих запросов, выбери нужный', reply_markup = await keyboard.get_markup())
            await callback_query.answer()
            await state.update_data(index_your_poll=dicters_p)

        elif callback_query.data[:4] == 'id_p':

            record = data.get('index_your_poll')
            id_p = callback_query.data[4:]
            if not record:
                await callback_query.message.answer('Проиозшла ошибка, попробуй заново')
                return None
            record = record[id_p]
            options = await format_json_f(record['variants'])
            if record['url']:
                keyboard = CallBackMarkup({'URL': record['url']}, row=1, additional_data='url')
                message_poll = await callback_query.message.answer_poll(question=record['description'],
                                    options=list(options.keys()),
                                    allows_multiple_answers=record['multiple_choice'],
                                    is_anonymous=True, reply_markup=await keyboard.get_markup())
            else:
                message_poll = await callback_query.message.answer_poll(question=record['description'],
                                    options=list(options.keys()),
                                    allows_multiple_answers=record['multiple_choice'],
                                    is_anonymous=True)

            await callback_query.message.answer(await format_for_str(options, record['vote'], record['max_vote']))
            await callback_query.answer()
            
        else:
            await callback_query.message.answer("Кажется, что произошел сбой, попробуйте /start")
            

@dp.message(Form.create_bonus)
async def create_bonus(message: Message, state: FSMContext) -> None:
    text = message.text
    async with AdminWork(message.from_user.id) as admin:
        sp_bonus = text.split('@@@')
        dicters = {'url': sp_bonus[0], 'type': sp_bonus[1], 'chat_id': int(sp_bonus[2]), 'money': int(sp_bonus[3])}
        await admin.add_chanel(dicters)
        await message.answer('Бонус добавлен')
        await state.clear()


@dp.message(Form.delete_bonus)
async def delete_bomus(message: Message, state: FSMContext) -> None:
    text = message.text
    async with  AdminWork(message.from_user.id) as admin:
        await admin.delete_chanel(text)
        await message.answer('Бонус удален')
        await state.clear()

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
            await state.clear()

@dp.message(Form.create_poll)
async def step_1_create_poll(message: Message, state: FSMContext) -> None:
    poll = message.poll
    data = await state.get_data() 
    async with data.get('con_user') as con_user:
        if poll:
            dicter = {
                'question': poll.question,
                'options': {i: 0 for i in list(map(lambda x: x.text, poll.options))},
                'anonymous': True,
                'multiple': poll.allows_multiple_answers,
            }
            res = {e: f'p_topic_{e}'  for e in (map(lambda x: x['topic_name'], await con_user.get_theam()))}
            keyboard = CallBackMarkup(res, 3)
            await message.reply('Отлично, теперь выбери тему к которой это относиться, если нет подходящей пиши @Regqwe',  reply_markup = await keyboard.get_markup())
            await state.update_data(data_poll=dicter)
        else:
            await message.answer('Это не опрос, попробуй заново')


@dp.message(Form.create_poll_step_3)
async def step_3_create_poll(message: Message, state: FSMContext) -> None:
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
    await state.set_state(Form.create_poll_step_2)
    await message.answer('Хорошо, отправь кол-во голосов, до которого будут проводиться голоса максимум 10000')


@dp.message(Form.create_poll_step_2)
async def step_2_create_poll(message: Message, state: FSMContext) -> None:
    count = message.text
    try:
        count = int(count)
        if type(count) is int and count < 10000:
            await state.update_data(max_vote=count)
            data = await state.get_data()
            data_p = data.get('data_poll')
            con_user = data.get('con_user')
            if data.get('url'):
                keyboard_to = CallBackMarkup({'URL': data['url']}, 1, additional_data='url') 
                await message.answer_poll(
                    question=data_p['question'],
                    options=list(data_p['options'].keys()),
                    is_anonymous=data_p['anonymous'],
                    allows_multiple_answers=data_p['multiple'], reply_markup= await keyboard_to.get_markup()
            )
            else:
                await message.answer_poll(
                    question=data_p['question'],
                    options=list(data_p['options'].keys()),
                    is_anonymous=data_p['anonymous'],
                    allows_multiple_answers=data_p['multiple']),
            keyboard = CallBackMarkup({'Принять': '1.2.Yes', 'Отклонить': '1.2.No'}, 2)    
            await message.answer(f'отлично, вот как будет выглядить опрос у других', reply_markup= await keyboard.get_markup())
        else:
            raise ValueError
    except ValueError as e:
        await message.answer(f'Введи правильное количество {count}')


@dp.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer, state: FSMContext):
    data = await state.get_data()
    Con = data.get('con_user')
    if not Con:
        return
    async with Con as con:
        poll = data.get('poll')
        await bot.stop_poll(chat_id=poll[0].chat.id, message_id=poll[0].message_id, reply_markup=poll[0].reply_markup)
        opt_d_1 = {i: i2 for i, i2 in enumerate(list(poll[1].keys()))}
        for option_id in  poll_answer.option_ids:
            poll[1][opt_d_1[option_id]] += 1
        await con.update_tables(await format_json(poll[1]), poll[2])


async def main():
    dp.message.register(create_bonus, StateFilter(Form.create_bonus))
    dp.message.register(delete_bomus, StateFilter(Form.delete_bonus))
    dp.message.register(process_name, StateFilter(Form.create_theam))
    dp.message.register(step_1_create_poll, StateFilter(Form.create_poll))
    dp.message.register(step_3_create_poll, StateFilter(Form.create_poll_step_3))
    dp.message.register(step_2_create_poll, StateFilter(Form.create_poll_step_2))
    await dp.start_polling(bot, allowed_updates=["message", "callback_query", "poll_answer"])


if __name__ == '__main__':
    asyncio.run(main()) 