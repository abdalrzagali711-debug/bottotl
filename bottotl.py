import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient

# --- الإعدادات الخاصة بك ---
TOKEN = "8597943520:AAEbCQj9Z-91dim6bkKMTVitKklCKo421Ms" 
# الرابط المستخرج من صورتك (جاهز للعمل)
MONGO_URL = "mongodb+srv://abdalrzagDB:10010207966##@cluster0.fighoyv.mongodb.net/?retryWrites=true&w=majority"
ADMIN_ID = 5524416062 # ضع هنا رقم الآيدي الخاص بك في تلجرام

# الاتصال بقاعدة بيانات MongoDB
client = MongoClient(MONGO_URL)
db = client['MegaBot_DB']
users_col = db['users']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- دالة البداية (Start) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # تسجيل المستخدم في قاعدة البيانات
    if not users_col.find_one({"user_id": user.id}):
        users_col.insert_one({"user_id": user.id, "name": user.first_name, "username": user.username})
    
    keyboard = [
        [InlineKeyboardButton("🎬 تحميل وسائط", callback_data='downloader'),
         InlineKeyboardButton("🤖 ذكاء اصطناعي", callback_data='ai')],
        [InlineKeyboardButton("🔄 تحويل ملفات", callback_data='files'),
         InlineKeyboardButton("🛡 فحص روابط", callback_data='security')],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data='my_stats')]
    ]
    
    # إظهار زر لوحة التحكم للمطور فقط
    if user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("🔐 لوحة التحكم (للمطور)", callback_data='admin_main')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🔥 أهلاً بك يا {user.first_name} في البوت الشامل 2026!\nأقوى الأدوات في مكان واحد. اختر خدمتك الآن:",
        reply_markup=reply_markup
    )

# --- لوحة التحكم الموسعة للمطور ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    total_users = users_col.count_documents({})
    
    text = (f"🛠 **غرفة التحكم للمطور**\n\n"
            f"👥 إجمالي المستخدمين: {total_users}\n"
            f"⚡️ حالة السيرفر: يعمل بنشاط (Render)\n"
            f"📅 التاريخ: 2026-01-18")
    
    keyboard = [
        [InlineKeyboardButton("📢 إذاعة رسالة (Broadcast)", callback_data='start_bc')],
        [InlineKeyboardButton("🚫 حظر مستخدم", callback_data='ban_user'),
         InlineKeyboardButton("🎁 تفعيل Premium", callback_data='make_prem')],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data='back_home')]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# --- نظام الإذاعة (Broadcast) ---
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("📥 أرسل الآن الرسالة (نص، صورة، فيديو) لإذاعتها للجميع:")
    context.user_data['state'] = 'waiting_for_bc'

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') == 'waiting_for_bc' and update.effective_user.id == ADMIN_ID:
        all_users = users_col.find({})
        count = 0
        for u in all_users:
            try:
                await context.bot.copy_message(chat_id=u['user_id'], from_chat_id=ADMIN_ID, message_id=update.message.message_id)
                count += 1
            except: pass
        await update.message.reply_text(f"✅ تم الإرسال بنجاح إلى {count} مستخدم.")
        context.user_data['state'] = None
    else:
        await update.message.reply_text("جاري معالجة طلبك... انتظر قليلاً ⏳")

# --- تشغيل البوت ---
def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(admin_panel, pattern='admin_main'))
    application.add_handler(CallbackQueryHandler(start_broadcast, pattern='start_bc'))
    application.add_handler(MessageHandler(filters.ALL, handle_all_messages))
    
    print("🚀 البوت الآن متصل بقاعدة MongoDB وجاهز للعمل!")
    application.run_polling()

if __name__ == '__main__':
    main()