import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "7587621989:AAE88oSfysl5IGjt7Mw7wPGETeblOo-c6Bo"

bot_running = True
public_replies = {}
private_replies = {}

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("▶️ تشغيل", callback_data="start"),
         InlineKeyboardButton("⛔ إيقاف", callback_data="stop")],
        [InlineKeyboardButton("💬 الردود العامة", callback_data="public"),
         InlineKeyboardButton("🔐 الردود الخاصة", callback_data="private")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎮 لوحة تحكم البوت:", reply_markup=get_main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    global bot_running
    
    if query.data == "start":
        bot_running = True
        await query.edit_message_text("✅ تم تشغيل البوت!", reply_markup=get_main_keyboard())
    
    elif query.data == "stop":
        bot_running = False
        await query.edit_message_text("⛔ تم إيقاف البوت!", reply_markup=get_main_keyboard())
    
    elif query.data == "public":
        await query.edit_message_text("💬 أرسل الكلمة العامة ثم الرد الخاص بها.\n\nيمكنك استخدام الكلمات:\n"
                                      "{id} - ID\n{name} - الاسم\n{username} - اليوزر\n{bio} - البايو\n"
                                      "{messages} - عدد الرسائل\n{joined} - تاريخ الانضمام\n{level} - المستوى\n{title} - اللقب\n{activity} - النشاط")
        context.user_data['mode'] = 'add_public'
    
    elif query.data == "private":
        await query.edit_message_text("🔐 أرسل الكلمة الخاصة ثم الرد الخاص بها.\nنفس الكلمات الديناميكية متوفرة.")
        context.user_data['mode'] = 'add_private'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_running:
        return
    
    text = update.message.text
    user = update.message.from_user
    mode = context.user_data.get("mode")
    
    if mode == "add_public":
        context.user_data['key'] = text
        await update.message.reply_text("✍️ أرسل الرد المرتبط بهذه الكلمة:")
        context.user_data['mode'] = 'save_public'
        return

    elif mode == "save_public":
        key = context.user_data.get('key')
        public_replies[key] = text
        await update.message.reply_text(f"✅ تم حفظ رد عام لـ {key}")
        context.user_data['mode'] = None
        return

    elif mode == "add_private":
        context.user_data['key'] = text
        await update.message.reply_text("✍️ أرسل الرد المرتبط بهذه الكلمة:")
        context.user_data['mode'] = 'save_private'
        return

    elif mode == "save_private":
        key = context.user_data.get('key')
        private_replies[key] = text
        await update.message.reply_text(f"✅ تم حفظ رد خاص لـ {key}")
        context.user_data['mode'] = None
        return

    # الردود التلقائية
    elif text in public_replies:
        reply = public_replies[text]
        await update.message.reply_text(apply_dynamic_placeholders(reply, user))

    elif text in private_replies and update.message.chat.type == "private":
        reply = private_replies[text]
        await update.message.reply_text(apply_dynamic_placeholders(reply, user))

def apply_dynamic_placeholders(reply: str, user) -> str:
    return reply.format(
        id=user.id,
        name=user.first_name,
        username=f"@{user.username}" if user.username else "بدون يوزر",
        bio="❓",  # سيتم تطويرها لاحقًا
        messages="❓",
        joined="❓",
        edits="❓",
        level="❓",
        title="❓",
        activity="❓"
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
