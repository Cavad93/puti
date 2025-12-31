"""
Базовые обработчики команд
"""
from telegram import Update
from telegram.ext import ContextTypes


class BaseHandler:
    """Базовые команды бота"""

    def __init__(self, db, keyboards):
        self.db = db
        self.keyboards = keyboards

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        await self.db.add_user(user.id, user.username, user.first_name)

        welcome_text = (
            f"Привет, {user.first_name}! 👋\n\n"
            "Я твой личный финансовый помощник с AI-мозгом. 🤖\n\n"
            "Моя цель - помочь тебе:\n"
            "✅ Выбраться из долгов\n"
            "✅ Накопить подушку безопасности\n"
            "✅ Контролировать расходы\n"
            "✅ Достичь финансовой свободы\n\n"
            "Давай начнем! Используй меню ниже 👇"
        )

        await update.message.reply_text(
            welcome_text,
            reply_markup=self.keyboards.main_menu()
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = (
            "📚 ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ\n\n"
            "💰 ДОХОДЫ:\n"
            "Добавляйте все источники дохода с категориями\n\n"
            "📊 РАСХОДЫ:\n"
            "Указывайте тип (обязательные/необязательные) и категорию\n"
            "Бот спросит, регулярный ли это расход\n\n"
            "💳 КРЕДИТЫ:\n"
            "Добавьте все кредиты, займы и кредитные карты\n"
            "Система автоматически рассчитает графики платежей\n\n"
            "🎯 БЮДЖЕТ:\n"
            "AI создаст персональный бюджет на основе ваших данных\n\n"
            "📈 ОТЧЕТЫ:\n"
            "Получайте отчеты с графиками за любой период\n\n"
            "🤖 AI-СОВЕТНИК:\n"
            "Задавайте вопросы, получайте рекомендации и стратегии\n\n"
            "Используйте /menu для вызова главного меню"
        )

        await update.message.reply_text(help_text)

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /menu"""
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=self.keyboards.main_menu()
        )

    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопок главного меню"""
        text = update.message.text

        if text == '💰 Добавить доход':
            await update.message.reply_text(
                "Выберите категорию дохода:",
                reply_markup=self.keyboards.income_category_menu()
            )

        elif text == '📊 Добавить расход':
            await update.message.reply_text(
                "Выберите тип расхода:",
                reply_markup=self.keyboards.expense_type_menu()
            )

        elif text == '💳 Мои кредиты':
            await update.message.reply_text(
                "Управление кредитами и займами:",
                reply_markup=self.keyboards.loan_management_menu()
            )

        elif text == '💳 Кредитные карты':
            await update.message.reply_text(
                "Управление кредитными картами:",
                reply_markup=self.keyboards.credit_card_menu()
            )

        elif text == '📈 Отчеты':
            await update.message.reply_text(
                "Выберите тип отчета:",
                reply_markup=self.keyboards.reports_menu()
            )

        elif text == '🎯 Бюджет':
            await update.message.reply_text(
                "Управление бюджетом:",
                reply_markup=self.keyboards.budget_menu()
            )

        elif text == '🤖 Спросить AI':
            await update.message.reply_text(
                "Что вы хотите узнать?",
                reply_markup=self.keyboards.ai_menu()
            )

        elif text == '⚙️ Настройки':
            await update.message.reply_text(
                "Настройки:",
                reply_markup=self.keyboards.settings_menu()
            )

        else:
            await update.message.reply_text(
                "Используйте кнопки меню для навигации",
                reply_markup=self.keyboards.main_menu()
            )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback кнопок"""
        query = update.callback_query
        await query.answer()

        if query.data == "back_main":
            await query.edit_message_text(
                "Главное меню:",
                reply_markup=self.keyboards.main_menu()
            )
