from aiogram import Router, F
from aiogram import flags
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from keyboards.user_keyboards import create_subscription_keyboard, check_user_subscription
from keyboards.user_keyboards import main,create_faculty_url,create_subscription_keyboard
from create_bot import bot
from dotenv import load_dotenv
import asyncio
import random
import logging
from html import escape as html_escape

load_dotenv()

start_router = Router()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

async def handle_register(message: Message, db_handler):
    # Допустим, вы получаете данные пользователя из message.from_user
    u = message.from_user
    # Добавляем пользователя с 'умным' выбором факультета (db_handler.add_user сама выберет faculty, если None)
    ok = await db_handler.add_user(u.id, username=u.username, first_name=u.first_name, last_name=u.last_name, is_bot=u.is_bot, language_code=getattr(u, 'language_code', None))
    if ok:
        await message.answer('Регистрация завершена.')
    else:
        await message.answer('Ошибка при регистрации. Попробуйте позже.')


# Команда /start - отправляем сообщение с предложением подписаться
@start_router.message(Command("start"))
async def start_command(message: Message):
    text = (
        """⚡️ Welcome to the Hogwarts Sorting Bot!⚡️  
    
🏰 Hogwarts’ga xush kelibsiz! Bu yerda sizni 4 ta sehrli fakultet kutmoqda:  

🦁 Gryffindor – jasorat va qat’iyat  
🐍 Slytherin – makr va yetakchilik  
🦅 Ravenclaw – bilim va donolik  
🦡 Hufflepuff – mehnatsevarlik va sadoqat  

🔮 Saralovchi shlyapa sizni qaysi fakultetga tegishli ekaningizni aniqlab beradi.  

🎉 Tayyormisiz? Keling, sehrli safarni boshlaymiz!"""
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

@start_router.message(F.text == "⚙️ Sozlamalar")
async def settings_menu(message: Message):
    await message.delete()
    # Сначала проверяем подписку
    if not await check_user_subscription(bot, message.from_user.id):
        await message.answer(
            "❌ Kirish cheklangan! Kanalga obuna bo'ling:",
            reply_markup=await create_subscription_keyboard()
        )
        return

    await message.answer("""Bu yerda siz botdan foydalanish uslubingizni moslashingiz mumkin:  

👤 Profilim — Fakultetingiz, ismingiz va ballaringizni ko‘rish.  
🔔 Xabarnomalar — Reyting va musobaqa yangiliklari haqida bildirishnomalarni yoqish/o‘chirish.  
🌐 Til — Bot interfeysini o‘zbekcha / inglizcha / ruscha tanlash.  
🎨 Tema — Bot dizaynini “yorug‘” yoki “qorong‘i” rejimga o‘tkazish.""")


@start_router.message(F.text == "❓ Yordam")
async def support_menu(message: Message):
    await message.delete()
    # Сначала проверяем подписку
    if not await check_user_subscription(bot, message.from_user.id):
        await message.answer(
            "❌ Kirish cheklangan! Kanalga obuna bo'ling:",
            reply_markup=await create_subscription_keyboard()
        )
        return

    await message.answer("""
🎓 Fakultet tanlash — Sizni 4 ta fakultetdan biriga ajratadi.  
📊 Reyting — Fakultetlarning umumiy ballari va natijalarini ko‘rsatadi.  
ℹ️ Loyiha haqida — Ushbu loyihaning maqsadi va vazifalari bilan tanishtiradi.  
⚙️ Sozlamalar — Shaxsiy sozlamalarni o‘zgartirish imkonini beradi.  
🎮 O‘yinlar — Qiziqarli mini-o‘yinlar orqali vaqtni maroqli o‘tkazish imkoniyati.  

❓ Agar qo‘shimcha savollaringiz bo‘lsa yoki muammo yuzaga kelsa, admin bilan bog‘laning:  
👤 Admin: @PSU_Admin""")


@start_router.message(F.text == '📝 Fakultetga qoshilish')
@flags.chat_action('typing')
async def get_faculty(message: Message, **data):
    await message.delete()
    msg = await message.answer('*Thinking...*', parse_mode='Markdown')

    # Имитация печати через ChatAction.typing + точки как у людей с рандомной задержкой
    texts = [
        "*Hmm.*",
        "*Hmm..*",
        "*Hmm...*",
        "*....*",
        "*.....*",
        "*Qiziq..*",
        "*Albatta!!*"
    ]

    for t in texts:
        try:
            await message.bot.send_chat_action(message.chat.id, action='typing')
            await asyncio.sleep(random.uniform(0.8, 1.5))
            await msg.edit_text(t, parse_mode='Markdown')
        except Exception as e:
            print(f"Ошибка редактирования: {e}")
            break

    db = data["db"]
    user = await db.get_user(message.from_user.id)

    if not user:
        await handle_register(message, db)
        user = await db.get_user(message.from_user.id)

    faculty_val = user.get('faculty') or 'Неизвестно'
    # Экранируем значение факультета перед отправкой в HTML parse_mode
    faculty_safe = html_escape(str(faculty_val))

    if user:
        try:
            await message.answer(f'📚 Вы из факультета "<b>{faculty_safe}</b>"', parse_mode='HTML')
        except Exception as e:
            logger.exception(f"Error sending faculty message: {e}")
    else:
        await message.answer("*❌ Foydalanuvchi ma'lumotlar bazasida topilmadi.*", parse_mode='Markdown')

    # Защита: если faculty отсутствует или равен None, присваиваем и обновляем
    if user and ("faculty" not in user or user["faculty"] is None):
        await db.add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            is_bot=message.from_user.is_bot,
            language_code=message.from_user.language_code,
            faculty=None
        )


@start_router.message(F.text == '📊 Reyting')
async def get_rating(message: Message, **data):
    await message.delete()
    await message.answer("""📊 Reyting

Hozircha reyting mavjud emas. 🔎  
Lekin tez orada bu bo‘limda fakultetlarning umumiy ballari, yetakchilar va musobaqa natijalari joylanadi! 🏆✨  

⏳ Kuzatib boring, sizning har bir ishtirokingiz fakultetingiz reytingiga ta’sir qiladi.   (deb chiqishi kerak)""")
#    db = data["db"]
#    user = await db.get_user(message.from_user.id)
#    if not user:
#        await start_handler(message, db)
#        user = await db.get_user(message.from_user.id)
#    if user:
#        await message.answer(f'Ваш рейтинг: {user.get("rating", "Нет рейтинга")}')
#    else:
#        await message.answer('Пользователь не найден в базе данных.')


@start_router.message(F.text == 'ℹ️ Loyiha haqida')
async def get_info(message: Message):
    await message.delete()
    await message.answer(
        """<b>ℹ️ Loyiha haqida</b>

🏫 Ushbu loyiha Shayxontohur TIM maktabi o'quvchilari orasida <b>do'stlik</b>, <b>sog'lom raqobat</b> va <b>jamoaviylikni rivojlantirish</b> maqsadida PSU (Presidential Student Union, @Shayxontohur_TIM) jamoasi tomonidan tashkil etilgan.

🔮 <b>Garri Potter'dagi Hogwarts an'analari asosida o'quvchilar 4 fakultetga ajratiladi:</b>
🦁 Gryffindor – <i>jasorat va qat'iyat</i>
🐍 Slytherin – <i>makr va yetakchilik</i>
🦅 Ravenclaw – <i>bilim va donolik</i>
🦡 Hufflepuff – <i>mehnatsevarlik va sadoqat</i>

🎯 <b>Loyihaning asosiy maqsadlari:</b>
- <i>O'quvchilar o'rtasida ijobiy raqobat yaratish</i>
- <i>Jamoaviy ishlashni kuchaytirish</i>
- <i>Bilim, salohiyat, volontyorlik, ijod va ijtimoiy sohalarda musobaqalar o'tkazish</i>
- <i>Eng faol va muvaffaqiyatli fakultetni aniqlash</i>

🏆 <b>Fakultetlar turli tadbirlarda ball to'plashadi va yil yakunida eng ko'p ball yig'gan fakultet Chempion deb e'lon qilinadi.</b>

✨ <b>Bu loyiha</b> — <i>o'quvchilarning qiziqishini oshirish, liderlik va do'stlikni mustahkamlash uchun yaratilgan maxsus dasturdir.</i>""",
        parse_mode='HTML'
    )
