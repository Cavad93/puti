"""Обработчик управления кредитами"""
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

class LoanHandler:
    def __init__(self, db, keyboards, calculator, claude):
        self.db = db
        self.keyboards = keyboards
        self.calculator = calculator
        self.claude = claude

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "add_loan":
            await query.edit_message_text("Выберите тип кредита:", reply_markup=self.keyboards.loan_type_menu())
        elif query.data == "list_loans":
            loans = await self.db.get_active_loans(query.from_user.id)
            if loans:
                await query.edit_message_text("Ваши кредиты:", reply_markup=self.keyboards.loan_list_menu(loans))
            else:
                await query.edit_message_text("У вас пока нет кредитов", reply_markup=self.keyboards.back_menu("back_main"))
        elif query.data == "debt_strategy":
            await self.show_debt_strategy(query, context)

    async def show_debt_strategy(self, query, context):
        user_id = query.from_user.id
        loans = await self.db.get_active_loans(user_id)

        if not loans:
            await query.edit_message_text("У вас нет активных кредитов", reply_markup=self.keyboards.back_menu("back_main"))
            return

        debts = [{'name': l['name'], 'balance': l['current_balance'], 'rate': l['interest_rate'], 'monthly_payment': l['monthly_payment']} for l in loans]

        comparison = self.calculator.compare_strategies(debts, 0)

        text = "🎯 СТРАТЕГИИ ПОГАШЕНИЯ ДОЛГОВ\n\n"
        text += f"💡 Рекомендуется: {comparison['recommended'].upper()}\n\n"
        text += f"📊 Снежный ком: {comparison['snowball']['total_months']} мес\n"
        text += f"📊 Лавина: {comparison['avalanche']['total_months']} мес\n\n"
        text += f"💰 Экономия с лавиной: {comparison['savings_with_avalanche']:,.2f} руб."

        await query.edit_message_text(text, reply_markup=self.keyboards.back_menu("back_loan_menu"))
