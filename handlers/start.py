from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from keyboards.user_keyboards import create_subscription_keyboard, check_user_subscription
from keyboards.user_keyboards import main,create_faculty_url,create_subscription_keyboard
from create_bot import bot
from dotenv import load_dotenv

load_dotenv()

start_router = Router()

async def start_handler(message: Message, db):
    user = message.from_user
    faculty = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin']
    index = await db.get_users_count() + 1
    faculty_value = faculty[index % 4]
    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
        faculty=faculty_value
    )
    await db.add_message(
        user_id=user.id,
        message_id=message.message_id,
        text=message.text
    )

# Команда /start - отправляем сообщение с предложением подписаться
@start_router.message(Command("start"))
async def start_command(message: Message):
    text = (
        "👋 Hush kelibsiz!\n\n"
        "Botdan foydalanish uchun kanalimizga obuna bo'lishingiz kerak..\n"
        "Obuna bo'lgandan so'ng, 'Obunani tekshirish' tugmasini bosing'."
    )
    await message.answer(
        text=text,
        reply_markup=await create_subscription_keyboard()
    )


# Обработка нажатия кнопки "Проверить подписку"
@start_router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    # Проверяем подписку
    is_subscribed = await check_user_subscription(bot, user_id)

    if is_subscribed:
        # Пользователь подписан - показываем главное меню
        await callback_query.message.edit_text(
            "✅ Ajoyib! Siz kanalga obuna bo'ldingiz.\n"
            "Endi siz botdan foydalanishingiz mumkin!",
            reply_markup=None
        )
        await callback_query.message.answer(
            "🎉 Xush kelibsiz! Amalni tanlang:",
            reply_markup=main
        )
    else:
        # Пользователь не подписан - показываем уведомление
        await callback_query.answer(
            "❌ Siz kanalga obuna bo'lmagansiz! Iltimos, obuna bo'ling va qayta urinib ko'ring.",
            show_alert=True
        )

    await callback_query.answer()


# Обработчики для кнопок главного меню
@start_router.message(F.text == "🎮 O\'yinlar")
async def main_menu(message: Message, **data):
    await message.delete()
    db = data["db"]
    user = await db.get_user(message.from_user.id)
    # Сначала проверяем подписку
    if not await check_user_subscription(bot, message.from_user.id):
        await message.answer(
            "❌ Kirish cheklangan! Kanalga obuna bo'ling:",
            reply_markup=await create_subscription_keyboard()
        )
        return

    await message.answer("O‘yinlar bo‘limiga xush kelibsiz!", reply_markup=await create_faculty_url(user.get("faculty", "Не назначен")))

@start_router.callback_query(F.data == "settings")
async def settings_menu(message: Message):
    await message.delete()
    # Сначала проверяем подписку
    if not await check_user_subscription(bot, message.from_user.id):
        await message.answer(
            "❌ Kirish cheklangan! Kanalga obuna bo'ling:",
            reply_markup=await create_subscription_keyboard()
        )
        return

    await message.answer("⚙️ Настройки бота...")


@start_router.callback_query(F.data == "help")
async def support_menu(message: Message):
    # Сначала проверяем подписку
    if not await check_user_subscription(bot, message.from_user.id):
        await message.answer(
            "❌ Kirish cheklangan! Kanalga obuna bo'ling:",
            reply_markup=await create_subscription_keyboard()
        )
        return

    await message.answer("Yordam ahahahahah")


@start_router.callback_query(F.data == 'faculty')
async def get_faculty(callback: CallbackQuery, **data):
    await callback.answer('Вы узнаете свой факультет!')
    db = data["db"]
    user = await db.get_user(callback.message.from_user.id)
    if not user:
        await start_handler(callback.message, db)
        user = await db.get_user(callback.message.from_user.id)
    if user:
        await callback.message.answer(f'Ваш факультет: {user.get("faculty", "Не назначен")}', reply_markup=main)
    else:
        await callback.message.answer('Пользователь не найден в базе данных.')
    # Защита: если faculty отсутствует или равен None, присваиваем и обновляем
    if user and ("faculty" not in user or user["faculty"] is None):
        faculty = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin']
        index = await db.get_users_count()
        faculty_value = faculty[index % 4]
        await db.add_user(
            user_id=callback.message.from_user.id,
            username=callback.message.from_user.username,
            first_name=callback.message.from_user.first_name,
            last_name=callback.message.from_user.last_name,
            is_bot=callback.message.from_user.is_bot,
            language_code=callback.message.from_user.language_code,
            faculty=faculty_value
        )
        user = await db.get_user(callback.message.from_user.id)


@start_router.callback_query(F.data == 'rating')
async def get_rating(callback: CallbackQuery, **data):
    await callback.answer('Вы узнаете свой рейтинг!')
    db = data["db"]
    user = await db.get_user(callback.message.from_user.id)
    if not user:
        await start_handler(callback.message, db)
        user = await db.get_user(callback.message.from_user.id)
    if user:
        await callback.message.answer(f'Ваш рейтинг: {user.get("rating", "Нет рейтинга")}')
    else:
        await callback.message.answer('Пользователь не найден в базе данных.')


@start_router.callback_query(F.data == 'get_info')
async def get_info(callback: CallbackQuery, **data):
    await callback.answer('Вы узнаете информацию о проекте!')
    db = data["db"]
    user = await db.get_user(callback.message.from_user.id)
    if not user:
        await start_handler(callback.message, db)
        user = await db.get_user(callback.message.from_user.id)
    if user:
        await callback.message.answer('Этот проект создан для сортировки пользователей по факультетам и отслеживании их рейтинга. Каждый пользователь автоматически распределяется на один из четырех факультетов: Gryffindor, Hufflepuff, Ravenclaw или Slytherin. Рейтинг пользователей обновляется на основе их активности в играх и достижений. Присоединяйтесь к нашему каналу, чтобы быть в курсе всех новостей и обновлений!')
    else:
        await callback.message.answer('Пользователь не найден в базе данных.')