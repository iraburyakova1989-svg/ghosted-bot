import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import google.generativeai as genai

TELEGRAM_TOKEN = "8774412957:AAGk2ywCIlK1jsXpqBfGZ5v--HiRCK92N_8"
GEMINI_KEY = "AIzaSyBZETK-1hm4DDmh5gZd_ClEC4vI7kJlOTY"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

Q1, Q2, Q3, Q4, Q5 = range(5)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")
    def log_message(self, *args):
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Он не запутался.\n*Ты просто не увидела правду.*\n\nОтветь на 5 вопросов — получишь честный разбор.", parse_mode="Markdown")
    kb = ReplyKeyboardMarkup([["Несколько недель", "1–3 месяца"], ["3–6 месяцев", "Полгода–год"], ["Больше года"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("*01 —* Как давно вы знакомы?", parse_mode="Markdown", reply_markup=kb)
    return Q1

async def q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q1"] = update.message.text
    kb = ReplyKeyboardMarkup([["Он перестал писать первым"], ["Отвечает, но редко и холодно"], ["Полностью пропал"], ["Сказал, что ему нужно время"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("*02 —* Кто исчез / взял дистанцию?", parse_mode="Markdown", reply_markup=kb)
    return Q2

async def q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q2"] = update.message.text
    kb = ReplyKeyboardMarkup([["Никогда", "Иногда, но редко"], ["Только по делу", "Иногда как раньше"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("*03 —* Он пишет первым сейчас?", parse_mode="Markdown", reply_markup=kb)
    return Q3

async def q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q3"] = update.message.text
    kb = ReplyKeyboardMarkup([["Да, официальные"], ["Что-то было, без статуса"], ["Флирт и близость"], ["Нет, только общение"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("*04 —* Были ли между вами отношения?", parse_mode="Markdown", reply_markup=kb)
    return Q4

async def q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q4"] = update.message.text
    await update.message.reply_text("*05 —* Что он сказал перед тем, как взять дистанцию?\n\n_Напиши своими словами._", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    return Q5

async def q5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q5"] = update.message.text
    d = context.user_data
    await update.message.reply_text("Анализирую...", reply_markup=ReplyKeyboardRemove())
    prompt = f"""Ты — жёсткий психоаналитик. Без сочувствия. Только правда. Обращайся на "ты". По-русски.
Знакомы: {d['q1']}. Что произошло: {d['q2']}. Пишет первым: {d['q3']}. Отношения: {d['q4']}. Сказал: "{d['q5']}".
Дай разбор в 4-5 коротких абзацах. Каждый — удар. Без утешений. Закончи мощной финальной фразой."""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
    except Exception as e:
        text = f"Ошибка: {e}"
    await update.message.reply_text(text)
    await update.message.reply_text("Хочешь разобрать другую ситуацию? Нажми /start")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши /start чтобы начать заново.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, q1)],
            Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, q2)],
            Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, q3)],
            Q4: [MessageHandler(filters.TEXT & ~filters.COMMAND, q4)],
            Q5: [MessageHandler(filters.TEXT & ~filters.COMMAND, q5)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
