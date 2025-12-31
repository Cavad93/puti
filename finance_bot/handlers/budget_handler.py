"""Обработчик управления бюджетом"""
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

class BudgetHandler:
    def __init__(self, db, keyboards, claude):
        self.db = db
        self.keyboards = keyboards
        self.claude = claude

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id

        if query.data == "show_budget":
            now = datetime.now()
            budget = await self.db.get_budget(user_id, now.month, now.year)

            if budget:
                text = f"💰 БЮДЖЕТ НА {now.strftime('%B %Y')}\n\n"
                text += f"Доход: {budget['total_income']:,.2f} руб.\n"
                text += f"Обязательные расходы: {budget['mandatory_expenses']:,.2f} руб.\n"
                text += f"Платежи по кредитам: {budget['loan_payments']:,.2f} руб.\n"
                text += f"Бюджет на необязательное: {budget['optional_budget']:,.2f} руб.\n\n"
                text += f"🎯 Подушка безопасности: {budget.get('emergency_fund_current', 0):,.2f} / {budget.get('emergency_fund_target', 0):,.2f} руб."
            else:
                text = "У вас еще нет бюджета. Создайте его с помощью AI!"

            await query.edit_message_text(text, reply_markup=self.keyboards.back_menu("back_main"))

        elif query.data == "create_budget_ai":
            await query.edit_message_text("🤖 Создаю персональный бюджет...")

            loans = await self.db.get_active_loans(user_id)
            loan_payments = sum(l['monthly_payment'] for l in loans)

            budget_text = await self.claude.create_monthly_budget(100000, 30000, loan_payments)

            await query.edit_message_text(f"💰 ВАШ БЮДЖЕТ:\n\n{budget_text}", reply_markup=self.keyboards.back_menu("back_main"))

        elif query.data == "financial_goals":
            goals = await self.db.get_active_goals(user_id)

            if goals:
                text = "🎯 ВАШИ ЦЕЛИ:\n\n"
                for goal in goals:
                    progress = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
                    text += f"• {goal['goal_type']}: {goal['current_amount']:,.2f} / {goal['target_amount']:,.2f} ({progress:.1f}%)\n"
            else:
                text = "У вас пока нет целей"

            await query.edit_message_text(text, reply_markup=self.keyboards.back_menu("back_main"))
