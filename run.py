import logging
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "6165423074:AAE1-cGJGMy0bsmKeEqJcKb9m0pGBUXT1tA"

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Функция для отображения календаря
def create_calendar(year: int, month: int):
    # Заголовки дней недели
    days_header = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    keyboard = [[InlineKeyboardButton(day, callback_data="ignore") for day in days_header]]

    # Вычисление дней месяца
    first_day = datetime(year, month, 1)
    first_weekday = (first_day.weekday() + 1) % 7  # Перемещение на понедельник
    days_in_month = (first_day + timedelta(days=31)).replace(day=1) - first_day

    # Генерация кнопок с числами
    days = [InlineKeyboardButton(" ", callback_data="ignore")] * first_weekday
    days += [
        InlineKeyboardButton(str(day), callback_data=f"date_{year}_{month}_{day}")
        for day in range(1, days_in_month.days + 1)
    ]

    # Преобразование в строки (недели)
    for i in range(0, len(days), 7):
        keyboard.append(days[i : i + 7])

    # Добавляем кнопки переключения месяца
    keyboard.append(
        [
            InlineKeyboardButton("<", callback_data=f"prev_{year}_{month}"),
            InlineKeyboardButton(">", callback_data=f"next_{year}_{month}"),
        ]
    )

    return InlineKeyboardMarkup(keyboard)

# Команда для отображения календаря
async def calendar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    await update.message.reply_text(
        "Выберите дату:",
        reply_markup=create_calendar(now.year, now.month),
    )

# Обработчик нажатий на кнопки календаря
async def calendar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    if callback_data.startswith("date_"):
        _, year, month, day = map(int, callback_data.split("_")[1:])
        selected_date = datetime(year, month, day).strftime("%Y-%m-%d")
        await query.edit_message_text(f"Вы выбрали дату: {selected_date}")
    elif callback_data.startswith("prev_"):
        _, year, month = map(int, callback_data.split("_")[1:])
        prev_month = datetime(year, month, 1) - timedelta(days=1)
        await query.edit_message_reply_markup(
            reply_markup=create_calendar(prev_month.year, prev_month.month)
        )
    elif callback_data.startswith("next_"):
        _, year, month = map(int, callback_data.split("_")[1:])
        next_month = datetime(year, month, 28) + timedelta(days=4)  # Переход к следующему месяцу
        await query.edit_message_reply_markup(
            reply_markup=create_calendar(next_month.year, next_month.month)
        )

# Игнорируем кнопки "пустых" ячеек
async def ignore_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("calendar", calendar_command))
    application.add_handler(CallbackQueryHandler(calendar_callback, pattern="^(date_|prev_|next_)"))
    application.add_handler(CallbackQueryHandler(ignore_callback, pattern="^ignore$"))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
