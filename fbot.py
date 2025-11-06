from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters

# Bosqichlar
NAME, PHONE, SURNAME, BIRTH, PASSPORT, TYPE, GENDER, VIDEO = range(8)

# Admin ID
ADMIN_ID = 8065400333  # Sizning Telegram ID

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Iltimos, ismingizni yozing:")
    return NAME

# Ismni olish
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    contact_button = KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
    keyboard = [[contact_button]]

    await update.message.reply_text(
        "Iltimos, telefon raqamingizni yuboring:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return PHONE

# Telefonni olish
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data["phone"] = update.message.contact.phone_number
    else:
        context.user_data["phone"] = update.message.text

    await update.message.reply_text("Familiyangizni yozing:")
    return SURNAME

# Familiyani olish
async def get_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["surname"] = update.message.text
    await update.message.reply_text("Tug‘ilgan sanangizni yozing (00.00.0000):")
    return BIRTH

# Tug‘ilgan sanani olish
async def get_birth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["birth"] = update.message.text
    await update.message.reply_text("Pasport seriya raqamingizni yozing (AA 0000000):")
    return PASSPORT

# Pasport
async def get_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["passport"] = update.message.text
    keyboard = [["Talaba", "Davlat xodimi"], ["Voyaga yetmagan", "Jismoniy shaxs"]]
    await update.message.reply_text(
        "Siz kimsiz?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return TYPE

# Kimligini olish
async def get_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["type"] = update.message.text
    keyboard = [["Erkak", "Ayol"]]
    await update.message.reply_text(
        "Jinsingizni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return GENDER

# Jinsni olish
async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text
    await update.message.reply_text("Iltimos, yuzingizni video xabar qilib yuboring 🎥")
    return VIDEO

# Video va yakun
async def get_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = context.user_data.get("name", "")
    phone = context.user_data.get("phone", "")
    surname = context.user_data.get("surname", "")
    birth = context.user_data.get("birth", "")
    passport = context.user_data.get("passport", "")
    user_type = context.user_data.get("type", "")
    gender = context.user_data.get("gender", "")

    info = f"""📋 Yangi surovnoma keldi!

👤 Ism: {name}
📞 Telefon: {phone}
👤 Familiya: {surname}
🎂 Tug‘ilgan sana: {birth}
🪪 Pasport: {passport}
💼 Kimligi: {user_type}
🚻 Jinsi: {gender}
🆔 Telegram: @{user.username if user.username else 'yo‘q'}

--------------------------
"""

    # 🔹 Ma’lumotlarni faylga saqlash
    with open("surovnoma.txt", "a", encoding="utf-8") as f:
        f.write(info)

    # 🔹 Admin’ga yuborish
    await context.bot.send_message(chat_id=ADMIN_ID, text=info)

    # 🔹 Video yuborish
    if update.message.video_note:
        await context.bot.send_video_note(chat_id=ADMIN_ID, video_note=update.message.video_note.file_id)
    elif update.message.video:
        await context.bot.send_video(chat_id=ADMIN_ID, video=update.message.video.file_id)

    # 🔹 Foydalanuvchiga javob
    await update.message.reply_text(
        "✅ Surovnoma qabul qilindi!\n\nOperatorlarimiz siz bilan tez orada bog‘lanishadi:"
    )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Surovnoma bekor qilindi.")
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token("8069081849:AAGgJ8XhrKyfm6lkp84EX6Yjin0_NzyOhMI").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_name)],
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, get_phone)],
            SURNAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_surname)],
            BIRTH: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_birth)],
            PASSPORT: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_passport)],
            TYPE: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_type)],
            GENDER: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_gender)],
            VIDEO: [MessageHandler(filters.VIDEO | filters.VIDEO_NOTE, get_video)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
