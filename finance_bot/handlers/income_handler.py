"""Обработчик управления доходами"""
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

class IncomeHandler:
    def __init__(self, db, keyboards):
        self.db = db
        self.keyboards = keyboards
        self.user_state = {}

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id

        if query.data.startswith("income_cat_"):
            category = query.data.replace("income_cat_", "")
            self.user_state[user_id] = {'category': category}
            await query.edit_message_text(
                f"Введите сумму дохода в категории '{category}' (в рублях):"
            )
            context.user_data['waiting_income_amount'] = True
