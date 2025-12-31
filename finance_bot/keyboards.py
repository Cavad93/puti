"""
Клавиатуры для Telegram бота
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from config import EXPENSE_CATEGORIES, INCOME_CATEGORIES, LOAN_TYPES


class Keyboards:
    """Класс для создания клавиатур"""

    @staticmethod
    def main_menu():
        """Главное меню"""
        keyboard = [
            ['💰 Добавить доход', '📊 Добавить расход'],
            ['💳 Мои кредиты', '💳 Кредитные карты'],
            ['📈 Отчеты', '🎯 Бюджет'],
            ['🤖 Спросить AI', '⚙️ Настройки']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def expense_type_menu():
        """Меню выбора типа расхода"""
        keyboard = [
            [InlineKeyboardButton("✅ Обязательные", callback_data="expense_type_mandatory")],
            [InlineKeyboardButton("⭐ Необязательные", callback_data="expense_type_optional")],
            [InlineKeyboardButton("❗ Незапланированные", callback_data="expense_type_unplanned")],
            [InlineKeyboardButton("« Назад", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def expense_category_menu(expense_type: str):
        """Меню выбора категории расхода"""
        categories = EXPENSE_CATEGORIES.get(expense_type, {})
        keyboard = []

        for category in categories.keys():
            keyboard.append([InlineKeyboardButton(category, callback_data=f"expense_cat_{category}")])

        keyboard.append([InlineKeyboardButton("« Назад", callback_data="back_expense_type")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def regular_expense_menu():
        """Меню вопроса о регулярности расхода"""
        keyboard = [
            [InlineKeyboardButton("✅ Да, регулярный", callback_data="regular_yes")],
            [InlineKeyboardButton("❌ Нет, разовый", callback_data="regular_no")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def income_category_menu():
        """Меню выбора категории дохода"""
        keyboard = []
        for category in INCOME_CATEGORIES:
            keyboard.append([InlineKeyboardButton(category, callback_data=f"income_cat_{category}")])

        keyboard.append([InlineKeyboardButton("« Назад", callback_data="back_main")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def loan_type_menu():
        """Меню выбора типа кредита"""
        keyboard = []
        for loan_type in LOAN_TYPES:
            callback = loan_type.lower().replace(' ', '_')
            keyboard.append([InlineKeyboardButton(loan_type, callback_data=f"loan_type_{callback}")])

        keyboard.append([InlineKeyboardButton("« Назад", callback_data="back_main")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def loan_management_menu():
        """Меню управления кредитами"""
        keyboard = [
            [InlineKeyboardButton("➕ Добавить кредит/займ", callback_data="add_loan")],
            [InlineKeyboardButton("📋 Список кредитов", callback_data="list_loans")],
            [InlineKeyboardButton("💵 Внести платеж", callback_data="make_payment")],
            [InlineKeyboardButton("🎯 Стратегия погашения", callback_data="debt_strategy")],
            [InlineKeyboardButton("« Назад", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def loan_list_menu(loans):
        """Меню со списком кредитов"""
        keyboard = []
        for loan in loans:
            loan_id = loan['id']
            name = loan['name']
            balance = loan['current_balance']
            keyboard.append([
                InlineKeyboardButton(
                    f"{name} - {balance:,.0f} руб.",
                    callback_data=f"loan_detail_{loan_id}"
                )
            ])

        keyboard.append([InlineKeyboardButton("« Назад", callback_data="back_loan_menu")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def loan_detail_menu(loan_id: int):
        """Меню деталей кредита"""
        keyboard = [
            [InlineKeyboardButton("💵 Внести платеж", callback_data=f"pay_loan_{loan_id}")],
            [InlineKeyboardButton("💰 Досрочное погашение", callback_data=f"early_pay_{loan_id}")],
            [InlineKeyboardButton("📊 График платежей", callback_data=f"schedule_{loan_id}")],
            [InlineKeyboardButton("🏖️ Кредитные каникулы", callback_data=f"holiday_{loan_id}")],
            [InlineKeyboardButton("❌ Закрыть кредит", callback_data=f"close_loan_{loan_id}")],
            [InlineKeyboardButton("« Назад", callback_data="list_loans")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def credit_card_menu():
        """Меню кредитных карт"""
        keyboard = [
            [InlineKeyboardButton("➕ Добавить карту", callback_data="add_card")],
            [InlineKeyboardButton("📋 Мои карты", callback_data="list_cards")],
            [InlineKeyboardButton("💳 Пополнить/Списать", callback_data="card_transaction")],
            [InlineKeyboardButton("« Назад", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def card_list_menu(cards):
        """Меню со списком кредитных карт"""
        keyboard = []
        for card in cards:
            card_id = card['id']
            bank = card['bank_name']
            balance = card['current_balance']
            limit = card['credit_limit']
            keyboard.append([
                InlineKeyboardButton(
                    f"{bank} - {balance:,.0f}/{limit:,.0f}",
                    callback_data=f"card_detail_{card_id}"
                )
            ])

        keyboard.append([InlineKeyboardButton("« Назад", callback_data="back_card_menu")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def card_detail_menu(card_id: int):
        """Меню деталей карты"""
        keyboard = [
            [InlineKeyboardButton("💰 Внести платеж", callback_data=f"pay_card_{card_id}")],
            [InlineKeyboardButton("💳 Списание с карты", callback_data=f"spend_card_{card_id}")],
            [InlineKeyboardButton("📊 Расчет процентов", callback_data=f"card_interest_{card_id}")],
            [InlineKeyboardButton("« Назад", callback_data="list_cards")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def reports_menu():
        """Меню отчетов"""
        keyboard = [
            [InlineKeyboardButton("📊 Отчет по расходам", callback_data="report_expenses")],
            [InlineKeyboardButton("💰 Отчет по доходам", callback_data="report_incomes")],
            [InlineKeyboardButton("💳 Отчет по долгам", callback_data="report_debts")],
            [InlineKeyboardButton("📈 Месячный сводный", callback_data="report_monthly")],
            [InlineKeyboardButton("🎯 Прогноз погашения", callback_data="report_forecast")],
            [InlineKeyboardButton("« Назад", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def report_period_menu():
        """Меню выбора периода отчета"""
        keyboard = [
            [InlineKeyboardButton("📅 Текущий месяц", callback_data="period_current_month")],
            [InlineKeyboardButton("📅 Прошлый месяц", callback_data="period_last_month")],
            [InlineKeyboardButton("📅 Последние 7 дней", callback_data="period_week")],
            [InlineKeyboardButton("📅 Последние 30 дней", callback_data="period_30days")],
            [InlineKeyboardButton("📅 Свой период", callback_data="period_custom")],
            [InlineKeyboardButton("« Назад", callback_data="back_reports")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def budget_menu():
        """Меню бюджета"""
        keyboard = [
            [InlineKeyboardButton("📊 Текущий бюджет", callback_data="show_budget")],
            [InlineKeyboardButton("🤖 Создать бюджет с AI", callback_data="create_budget_ai")],
            [InlineKeyboardButton("✏️ Ввести вручную", callback_data="create_budget_manual")],
            [InlineKeyboardButton("🎯 Цели", callback_data="financial_goals")],
            [InlineKeyboardButton("« Назад", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def ai_menu():
        """Меню AI-советника"""
        keyboard = [
            [InlineKeyboardButton("💡 Общий анализ ситуации", callback_data="ai_general")],
            [InlineKeyboardButton("📊 Анализ расходов", callback_data="ai_expenses")],
            [InlineKeyboardButton("🎯 Стратегия погашения долгов", callback_data="ai_debt_strategy")],
            [InlineKeyboardButton("💰 Помощь с бюджетом", callback_data="ai_budget")],
            [InlineKeyboardButton("❓ Свой вопрос", callback_data="ai_custom")],
            [InlineKeyboardButton("« Назад", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def settings_menu():
        """Меню настроек"""
        keyboard = [
            [InlineKeyboardButton("🔔 Настройки уведомлений", callback_data="settings_notifications")],
            [InlineKeyboardButton("📊 Статистика", callback_data="settings_stats")],
            [InlineKeyboardButton("❓ Помощь", callback_data="settings_help")],
            [InlineKeyboardButton("« Назад", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirm_menu(action: str, item_id: int = None):
        """Меню подтверждения действия"""
        callback_yes = f"confirm_{action}_{item_id}" if item_id else f"confirm_{action}"
        callback_no = f"cancel_{action}_{item_id}" if item_id else f"cancel_{action}"

        keyboard = [
            [InlineKeyboardButton("✅ Да, подтверждаю", callback_data=callback_yes)],
            [InlineKeyboardButton("❌ Отмена", callback_data=callback_no)]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def cancel_menu():
        """Меню с кнопкой отмены"""
        keyboard = [[InlineKeyboardButton("❌ Отменить", callback_data="cancel")]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_menu(callback: str = "back_main"):
        """Меню с кнопкой назад"""
        keyboard = [[InlineKeyboardButton("« Назад", callback_data=callback)]]
        return InlineKeyboardMarkup(keyboard)
