from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class CallBackMarkup:
    def __init__(self, dicters: dict, row: int, additional_data='callback_data'):
        self.sp, cash_sp, index_ = [], [], 0
        self.additional_data = additional_data
        self.dictr = dicters
        for key, values in dicters.items():
            if index_ == row:
                self.sp.append(cash_sp[:])
                cash_sp = []
                index_ = 0
            if additional_data == 'callback_data':
                cash_sp.append(InlineKeyboardButton(text=str(key), callback_data=str(values)))
            elif additional_data == 'url':
                cash_sp.append(InlineKeyboardButton(text=str(key), url=str(values)))
            index_ += 1
        else:
            self.sp.append(cash_sp[:])
        self.markup = InlineKeyboardMarkup(inline_keyboard=self.sp)

    async def other_param_add(self, value, key):
        if self.additional_data == 'callback_data':
            self.sp.append([InlineKeyboardButton(text=str(key), url=str(value))])
        else:
            self.sp.append([InlineKeyboardButton(text=str(key), callback_data=str(value))])
        self.markup = InlineKeyboardMarkup(inline_keyboard=self.sp)

    async def get_markup(self):
        return self.markup
  
    async def get_sp(self):
        return self.dictr

    async def __str__(self):
        return f'{self.sp}\n{self.dictr}'
        