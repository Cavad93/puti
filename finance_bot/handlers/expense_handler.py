"""Обработчик управления расходами"""
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

class ExpenseHandler:
    def __init__(self, db, keyboards):
        self.db = db
        self.keyboards = keyboards
        self.user_state = {}

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id

        if query.data.startswith("expense_type_"):
            expense_type = query.data.replace("expense_type_", "")
            self.user_state[user_id] = {'type': expense_type}
            await query.edit_message_text(
                "Выберите категорию:",
                reply_markup=self.keyboards.expense_category_menu(expense_type)
            )

        elif query.data.startswith("expense_cat_"):
            category = query.data.replace("expense_cat_", "")
            self.user_state[user_id]['category'] = category

            if self.user_state[user_id]['type'] == 'mandatory':
                await query.edit_message_text(
                    f"Это регулярный расход в категории '{category}'?",
                    reply_markup=self.keyboards.regular_expense_menu()
                )
            else:
                await query.edit_message_text(
                    f"Введите сумму расхода для '{category}' (в рублях):"
                )
                context.user_data['waiting_expense_amount'] = True

        elif query.data.startswith("regular_"):
            is_regular = query.data == "regular_yes"
            self.user_state[user_id]['is_regular'] = is_regular
            await query.edit_message_text(
                f"Введите сумму расхода (в рублях):"
            )
            context.user_data['waiting_expense_amount'] = True
