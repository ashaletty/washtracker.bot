from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import json
import os
from datetime import date, datetime

TOKEN = "7664682622:AAG6UJxhx7NgTN2sGgg8Uzh0Ng_-DDeVh2g"
FILE = "hygiene_data.json"


# ---------- логика (из твоего скрипта) ----------

def load_data():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def mark(action):
    data = load_data()
    today = date.today().isoformat()

    if action not in data:
        data[action] = {"count": 0, "last_date": None}

    data[action]["count"] += 1
    data[action]["last_date"] = today
    save_data(data)


def get_stats():
    data = load_data()
    today = date.today()

    if not data:
        return "Нет данных."

    lines = []
    for action, info in data.items():
        last = info["last_date"]
        if last:
            days_ago = (today - datetime.fromisoformat(last).date()).days
        else:
            days_ago = "никогда"

        lines.append(f"{action}: {info['count']} раз, не делал {days_ago} дн.")

    return "\n".join(lines)


# ---------- telegram ----------

keyboard = ReplyKeyboardMarkup(
    [
        ["👐 Помыл руки", "🧼 Умылся"],
        ["🦷 Почистил зубы", "💪 Помыл подмышки"],
        ["📊 Статистика", "♻️ Обнулить"]
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Трекер гигиены запущен.",
        reply_markup=keyboard
    )


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "👐 Помыл руки":
        mark("помыл руки")
        await update.message.reply_text("хорош, помыл руки!👐")

    elif text == "🧼 Умылся":
        mark("умылся")
        await update.message.reply_text("Отмечено: умылся🧼")

    elif text == "🦷 Почистил зубы":
        mark("почистил зубы")
        await update.message.reply_text("Отмечено: почистил зубы🦷")

    elif text == "💪 Помыл подмышки":
        mark("помыл подмышки")
        await update.message.reply_text("Отмечено: помыл подмышки💪")

    elif text == "📊 Статистика":
        await update.message.reply_text(get_stats())

    elif text == "♻️ Обнулить":
        save_data({})
        await update.message.reply_text("Статистика обнулена.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))

    app.run_polling()


if __name__ == "__main__":
    main()

