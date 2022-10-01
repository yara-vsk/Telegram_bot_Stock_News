from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def company_keyboard(list_companies):
    markup = InlineKeyboardMarkup()
    for company in list_companies:
        button_text = f"{company}"
        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=f'company_name ={company}')
        )
    markup.insert(InlineKeyboardButton(text='Cancel', callback_data=f'cancel'))
    return markup

async def all_company_gpw(list_companies):
    markup = InlineKeyboardMarkup()
    for company in list_companies:
        button_text = f"{company}"
        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=f'company_name_in_gpw ={company}')
        )
    markup.insert(InlineKeyboardButton(text='Cancel', callback_data=f'Cancel_'))
    return markup