import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import google.generativeai as genai

# ── CONFIG ──────────────────────────────────────────────
TELEGRAM_TOKEN = "8774412957:AAGk2ywCIlK1jsXpqBfGZ5v--HiRCK92N_8"
GEMINI_KEY = "AIzaSyBZETK-1hm4DDmh5gZd_ClEC4vI7kJlOTY"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ── STATES ──────────────────────────────────────────────
Q1, Q2, Q3, Q4, Q5 = range(5)

QUESTIONS = [
    ("q1", "Как давно вы знакомы?", [["Несколько недель", "1–3 месяца"], ["3–6 месяцев", "Полгода–год"], ["Больше года"]]),
    ("q2", "Кто исчез / взял дистанцию?", [["Он перестал писать первым"], ["Отвечает, но редко и холодно"], ["Полностью пропал"], ["Сказал, что ему нужно время"]]),
    ("q3", "Он пишет первым сейчас?", [["Никогда", "Иногда, но редко"], ["Только по делу", "Иногда как раньше"]]),
    ("q4", "Были ли между вами отношения?", [["Да, официальные"], ["Что-то было, без статуса"], ["Флирт и близость"], ["Нет, только общение"]]),
]

# ── HANDLERS ────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Он не запутался.\n*Ты просто не увидела правду.*\n\nОпиши ситуацию — получишь честный разбор без утешений.",
        parse_mode="Markdown"
    )
    await asyncio.sleep(0.5)
    keyboard = ReplyKeyboardMarkup(QUESTIONS[0][2], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(f"*01 —* {QUESTIONS[0][1]}", parse_mode="Markdown", reply_markup=keyboard)
    return Q1

async def q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q1"] = update.message.text
    keyboard = ReplyKeyboardMarkup(QUESTIONS[1][2], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(f"*02 —* {QUESTIONS[1][1]}", parse_mode="Markdown", reply_markup=keyboard)
    return Q2

async def q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q2"] = update.message.text
    keyboard = ReplyKeyboardMarkup(QUESTIONS[2][2], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(f"*03 —* {QUESTIONS[2][1]}", parse_mode="Markdown", reply_markup=keyboard)
    return Q3

async def q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q3"] = update.message.text
    keyboard = ReplyKeyboardMarkup(QUESTIONS[3][2], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(f"*04 —* {QUESTIONS[3][1]}", parse_mode="Markdown", reply_markup=keyboard)
    return Q4

async def q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q4"] = update.message.text
    await update.message.reply_text(
        "*05 —* Что он сказал перед тем, как взять дистанцию?\n\n_Напиши своими словами. Буквально._",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return Q5

async def q5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q5"] = update.message.text
    d = context.user_data

    await update.message.reply_text("Анализирую...", reply_markup=ReplyKeyboardRemove())

    prompt = f"""Ты — жёсткий, прямолинейный психоаналитик. Без сочувствия. Без воды. Только правда. Обращайся к женщине на "ты". Пиши по-русски.

Ситуация:
- Знакомы: {d['q1']}
- Что произошло: {d['q2']}
- Пишет ли первым: {d['q3']}
- Были ли отношения: {d['q4']}
- Что он сказал перед дистанцией: "{d['q5']}"

Дай разбор в 4–5 коротких абзацах. Каждый абзац — удар. Никаких утешений. Говори о паттерне поведения мужчины, что он на самом деле означает, и что ей нужно принять как факт. Закончи одной мощной финальной фразой-выводом. Только текст, без заголовков и маркеров."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
    except Exception as e:
        text = f"Ошибка: {e}"

    await update.message.reply_text(text)
    await asyncio.sleep(1)
    await update.message.reply_text(
        "Хочешь разобрать другую ситуацию? Нажми /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Окей. Напиши /start чтобы начать заново.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ── MAIN ────────────────────────────────────────────────
def main():
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
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
