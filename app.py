from aiogram import executor
from load_all import bot, bn, db
from admin_panel import dp


async def on_shutdown(dp):
    await bot.close()

async def on_startup(dp):
    db.on_start_up()
    bn.all_companies_gpw()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup)

