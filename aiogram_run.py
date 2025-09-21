import asyncio
from create_bot import bot, dp, scheduler
from create_bot import pg_db
from work_time.time_func import send_time_msg

async def main():
    await pg_db.create_pool()
    await pg_db.init_database()
    scheduler.add_job(send_time_msg, 'interval', seconds=999999999)
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
