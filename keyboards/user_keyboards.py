from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, user

# Замени на ID твоего канала (должен начинаться с -100 для супергрупп/каналов)
CHANNEL_ID = "@Shayxontohur_TIM"  # или -1001234567890

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📝 Fakultetga qoshilish'),
     KeyboardButton(text='📊 Reyting')],
    [KeyboardButton(text='ℹ️ Loyiha haqida'),
     KeyboardButton(text='❓ Yordam')],
    [KeyboardButton(text='⚙️ Sozlamalar'),
     KeyboardButton(text='🎮 O\'yinlar'), ]

] ,resize_keyboard=True, input_field_placeholder='Bo\'limni tanlang...')

# Создаем inline клавиатуру с кнопкой подписки
async def create_subscription_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna boling", url=f"https://t.me/Shayxontohur_TIM")],
        [InlineKeyboardButton(text="✅ Obunani tekshiring", callback_data="check_subscription")]
    ])
    return keyboard

# Функция проверки подписки пользователя
async def check_user_subscription(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        # Проверяем статус пользователя в канале
        return member.status in ["creator", "administrator", "member"]
    except Exception as e:
        print(f"Obunani tekshirishda xatolik yuz berdi: {e}")
        return False

async def create_faculty_url(faculty: str) -> InlineKeyboardMarkup:
    # Большое превью
    # Для использования prefer_large_media обязательно указывать ещё и url
    options_3 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_large_media=True
    )
    await message.answer(
        f"Большое превью\n{links_text}",
        link_preview_options=options_3
    )
    url = f"https://t.me/joinchat/{faculty}"  # Замените на реальную ссылку для каждого факультета
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Join {faculty}", url=url)]
    ])
    return keyboard