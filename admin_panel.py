from asyncio import sleep
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, LabeledPrice, PreCheckoutQuery)
from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, message, ReplyKeyboardRemove, poll
from menu_keyboards import company_keyboard, all_company_gpw
from load_all import dp, bot, bn, db
from states import UrlEnter,MenuCompanies
import datetime
import random
import time
from pytz import timezone


@dp.message_handler(commands="start")
async def cancel(message: types.Message):
    id_telegram=message.from_user.id
    name_telegram=message.from_user.full_name
    db.create_user(id_telegram,name_telegram)
    await message.answer(f"Hi, {name_telegram}")


@dp.message_handler(commands="url")
async def cancel(message: types.Message):
    await message.answer("Proszę wprowadzić url spółki ze strony Bankier.pl z zakładki 'Podsumowanie'")
    await UrlEnter.Url_input.set()


@dp.message_handler(state=UrlEnter.Url_input)
async def enter_url(message: types.Message,state: FSMContext):
    url = message.text
    id_telegram = message.from_user.id
    bn.add_new_url_to_dict(url,id_telegram)
    await state.reset_state()


@dp.message_handler(commands="all")
async def user_all_comps(message: types.Message):
    id_telegram = message.from_user.id
    companies=db.user_all_companies(id_telegram)
    markup = await company_keyboard(companies)
    if companies == None or companies == []:
        await message.answer(f"You don't have any companies in subscriptions ")
        return
    await message.answer(f"You are subscribed to the following companies:\n", reply_markup=markup)
    return

@dp.message_handler(commands="users")
async def user_all_comps(message: types.Message):
    users=db.count_users()
    await message.answer(f"Now {users} users in Database")
    return


@dp.callback_query_handler(text_contains="company_name =")
async def menu_company(call: CallbackQuery):
    await call.message.edit_reply_markup()
    name_company = call.data[14:]
    company_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Last news", callback_data=f'last news={name_company}')],
            [
                InlineKeyboardButton(text="Last communicate", callback_data=f'last communicate={name_company}')],
            [
                InlineKeyboardButton(text="Unsubscribe", callback_data=f'unsubscribe={name_company}')],
            [
                InlineKeyboardButton(text="Cancel", callback_data=f'cancel')]
        ]
        )

    await call.message.answer(f"{name_company}", reply_markup=company_markup)
    return


@dp.callback_query_handler(text_contains="cancel")
async def cancel_callback(call: CallbackQuery):
    await call.message.edit_reply_markup()
    return


@dp.callback_query_handler(text_contains="unsubscribe=")
async def unsubscribe_company(call: CallbackQuery):
    await call.message.edit_reply_markup()
    name_company = call.data[12:]
    id_telegram=call.from_user.id
    db.delete_company_for_user(id_telegram,name_company)
    await call.message.answer(f"Cancel subscribe of {name_company}")
    return


@dp.callback_query_handler(text_contains="last news=")
async def last_news_company(call: CallbackQuery):
    await call.message.edit_reply_markup()
    name_company = call.data[10:]
    list_news=bn.news_company(name_company)
    await call.message.answer(f"{list_news[0]}\n{list_news[1]}")
    return


@dp.callback_query_handler(text_contains="last communicate=")
async def last_news_company(call: CallbackQuery):
    await call.message.edit_reply_markup()
    name_company = call.data[17:]
    list_news=bn.news_company(name_company)
    await call.message.answer(f"{list_news[2]}\n{list_news[3]}")
    return


@dp.message_handler(commands="add")
async def gpw_all_companies_first_letter(message: types.Message):
    companies=db.all_companies_gpw()
    markup = await all_company_gpw(companies)
    await message.answer(f"Select the first character of the company GPW name:\n", reply_markup=markup)
    await MenuCompanies.Menu1.set()

@dp.callback_query_handler(text_contains="company_name_in_gpw =",state=MenuCompanies.Menu1)
async def gpw_all_companies_for_character(call: CallbackQuery):
    await call.message.edit_reply_markup()
    name_company_character = call.data[21:]
    companies = db.all_companies_gpw_for_character(name_company_character)
    markup = await all_company_gpw(companies)
    await call.message.answer(f"Choose from the list of GPW companies to subscribe:\n", reply_markup=markup)
    await MenuCompanies.Menu1_out.set()

@dp.callback_query_handler(text_contains="Cancel_",state=MenuCompanies.Menu1)
async def gpw_cancel(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.reset_state()


@dp.callback_query_handler(text_contains="company_name_in_gpw =",state=MenuCompanies.Menu1_out)
async def gpw_all_companies_for_character(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    name_company = call.data[21:]
    id_telegram = call.from_user.id
    url_company=bn.url_bankier + db.return_url_for_company_gpw(name_company)
    href_last_news,href_last_communicate =bn.last_href_response_url(url_company)
    db.add_company_for_user(id_telegram=id_telegram,name_company=name_company,url_page=url_company,
                            href_last_news=href_last_news, href_last_communicate=href_last_communicate)
    await call.message.answer(f"You subscribed to the company {name_company}")
    await state.reset_state()


@dp.callback_query_handler(text_contains="Cancel_",state=MenuCompanies.Menu1_out)
async def gpw_cancel(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.reset_state()

@dp.message_handler(commands="t")
async def check_actualization(message: types.Message):
    if bn.status_actualization():
        await message.answer(f"Check actualization already activated")
        return
    while True:
        try:
            actualization_list = bn.check_aktualization_for_all_url()
        except ConnectionError:
            actualization_list = []
        if actualization_list:
            for actualization in actualization_list:
                for user in actualization[2]:
                    try:
                        await bot.send_message(user.id_telegram, f"{actualization[0]}\n{actualization[1]}")
                    except:
                        pass
        await message.answer(f"Actualization complete")
        now = datetime.datetime.now(tz=timezone('Europe/Warsaw'))
        if now.hour >= 16:
            timer = (86400 + 27000 + random.randrange(1, 45, 1)) - (now.hour * 60 * 60 + now.minute * 60 + now.second)
        else:
            timer = (57600 + random.randrange(1, 45, 1)) - (now.hour * 60 * 60 + now.minute * 60 + now.second)
        print(timer)
        print(now)
        await sleep(timer)


@dp.message_handler(commands="a")
async def check_actualization(message: types.Message):
    db.update_href_last_for_company(id_company=1,href_last_news='/wiadomosc/Orlen-podtrzymuje-9-5-mld-zl-inwestycji-w-2021-r-na-poczatku-maja-wniosek-do-UOKiK-ws-PGNiG-8103582.html')
    await message.answer(f"update")
    return


@dp.message_handler(commands="b")
async def check_actualization(message: types.Message):
    db.update_href_last_for_company(id_company=2,href_last_communicate='/wiadf')
    await message.answer(f"update2")
    return

@dp.message_handler(commands="c")
async def check_actualization(message: types.Message):
    db.update_href_last_for_company(id_company=3,href_last_communicate='/wiakkk')
    await message.answer(f"update3")
    return

@dp.message_handler(commands="up")
async def check_actualization(message: types.Message):
    try:
        actualization_list = bn.check_aktualization_for_all_url()
    except ConnectionError:
        actualization_list = []
    actualization_set=set()
    if actualization_list:
        for actualization in actualization_list:
            if actualization[1] in actualization_set:
                continue
            else:
                actualization_set.add(actualization[1])
                for user in actualization[2]:
                    try:
                        await bot.send_message(user.id_telegram, f"{actualization[0]}\n{actualization[1]}")
                    except:
                        pass
    await message.answer(f"Actualization complete")
    return

