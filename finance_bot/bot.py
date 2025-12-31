"""
Главный файл Telegram бота для управления финансами
"""
import logging
import asyncio
from datetime import datetime, time as datetime_time
import pytz

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, ALLOWED_USER_IDS, TIMEZONE, REMINDER_HOUR, REMINDER_MINUTE
from database import Database
from keyboards import Keyboards
from utils import ClaudeAdvisor, FinancialCalculator, ReportGenerator

# Импорт обработчиков
from handlers.base_handler import BaseHandler
from handlers.loan_handler import LoanHandler
from handlers.expense_handler import ExpenseHandler
from handlers.income_handler import IncomeHandler
from handlers.report_handler import ReportHandler
from handlers.ai_handler import AIHandler
from handlers.budget_handler import BudgetHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class FinanceBot:
    """Основной класс финансового бота"""

    def __init__(self):
        self.db = Database()
        self.keyboards = Keyboards()
        self.claude = ClaudeAdvisor()
        self.calculator = FinancialCalculator()
        self.reporter = ReportGenerator()

        # Инициализация обработчиков
        self.base_handler = BaseHandler(self.db, self.keyboards)
        self.loan_handler = LoanHandler(self.db, self.keyboards, self.calculator, self.claude)
        self.expense_handler = ExpenseHandler(self.db, self.keyboards)
        self.income_handler = IncomeHandler(self.db, self.keyboards)
        self.report_handler = ReportHandler(self.db, self.keyboards, self.reporter)
        self.ai_handler = AIHandler(self.db, self.keyboards, self.claude, self.calculator)
        self.budget_handler = BudgetHandler(self.db, self.keyboards, self.claude)

    def check_access(self, user_id: int) -> bool:
        """Проверка доступа пользователя"""
        if not ALLOWED_USER_IDS:
            logger.warning("ALLOWED_USER_IDS не настроен!")
            return False
        return user_id in ALLOWED_USER_IDS

    async def access_denied(self, update: Update, context):
        """Обработчик отказа в доступе"""
        await update.message.reply_text(
            "⛔ У вас нет доступа к этому боту.\n\n"
            f"Ваш ID: {update.effective_user.id}\n"
            "Обратитесь к администратору."
        )

    async def send_daily_reminder(self, context):
        """Отправка ежедневного напоминания"""
        for user_id in ALLOWED_USER_IDS:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="⏰ Время вносить данные за день!\n\n"
                         "Не забудьте записать:\n"
                         "• Все доходы\n"
                         "• Все расходы\n"
                         "• Платежи по кредитам\n\n"
                         "Финансовая дисциплина - ключ к свободе! 💪"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")

    def setup_handlers(self, app: Application):
        """Настройка обработчиков команд"""

        # Фильтр доступа
        def access_filter(func):
            async def wrapper(update: Update, context):
                if not self.check_access(update.effective_user.id):
                    await self.access_denied(update, context)
                    return
                return await func(update, context)
            return wrapper

        # Базовые команды
        app.add_handler(CommandHandler("start", access_filter(self.base_handler.start)))
        app.add_handler(CommandHandler("help", access_filter(self.base_handler.help)))
        app.add_handler(CommandHandler("menu", access_filter(self.base_handler.menu)))

        # Обработчик текстовых сообщений главного меню
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            access_filter(self.base_handler.handle_main_menu)
        ))

        # Обработчик callback кнопок
        app.add_handler(CallbackQueryHandler(
            access_filter(self.base_handler.handle_callback),
            pattern="^back_main$"
        ))

        # Callback для остальных модулей
        app.add_handler(CallbackQueryHandler(
            access_filter(self.loan_handler.handle_callback),
            pattern="^(loan|pay|early|schedule|holiday|close|debt_strategy)_"
        ))
        app.add_handler(CallbackQueryHandler(
            access_filter(self.expense_handler.handle_callback),
            pattern="^(expense|regular)_"
        ))
        app.add_handler(CallbackQueryHandler(
            access_filter(self.income_handler.handle_callback),
            pattern="^income_"
        ))
        app.add_handler(CallbackQueryHandler(
            access_filter(self.report_handler.handle_callback),
            pattern="^(report|period)_"
        ))
        app.add_handler(CallbackQueryHandler(
            access_filter(self.ai_handler.handle_callback),
            pattern="^ai_"
        ))
        app.add_handler(CallbackQueryHandler(
            access_filter(self.budget_handler.handle_callback),
            pattern="^(budget|create_budget|show_budget|financial_goals)_"
        ))

        # Обработчик ошибок
        app.add_error_handler(self.error_handler)

    async def error_handler(self, update: Update, context):
        """Обработка ошибок"""
        logger.error(f"Ошибка: {context.error}", exc_info=context.error)

        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка при обработке команды.\n"
                "Попробуйте еще раз или обратитесь к администратору."
            )

    async def post_init(self, app: Application):
        """Инициализация после запуска"""
        # Инициализация базы данных
        await self.db.init_db()
        logger.info("База данных инициализирована")

        # Настройка ежедневного напоминания
        job_queue = app.job_queue
        tz = pytz.timezone(TIMEZONE)
        reminder_time = datetime_time(hour=REMINDER_HOUR, minute=REMINDER_MINUTE, tzinfo=tz)

        job_queue.run_daily(
            self.send_daily_reminder,
            time=reminder_time,
            name="daily_reminder"
        )
        logger.info(f"Ежедневное напоминание настроено на {REMINDER_HOUR}:{REMINDER_MINUTE:02d} {TIMEZONE}")

    def run(self):
        """Запуск бота"""
        logger.info("Запуск финансового бота...")

        # Создание приложения
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(self.post_init).build()

        # Настройка обработчиков
        self.setup_handlers(app)

        # Запуск бота
        logger.info("Бот запущен!")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    bot = FinanceBot()
    bot.run()
