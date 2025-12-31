"""Обработчик AI-советника"""
from telegram import Update
from telegram.ext import ContextTypes

class AIHandler:
    def __init__(self, db, keyboards, claude, calculator):
        self.db = db
        self.keyboards = keyboards
        self.claude = claude
        self.calculator = calculator

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id

        await query.edit_message_text("🤔 Анализирую вашу ситуацию...")

        if query.data == "ai_general":
            await self.general_analysis(query, user_id)
        elif query.data == "ai_expenses":
            await self.expenses_analysis(query, user_id)
        elif query.data == "ai_debt_strategy":
            await self.debt_strategy(query, user_id)
        elif query.data == "ai_budget":
            await self.budget_help(query, user_id)
        elif query.data == "ai_custom":
            await query.edit_message_text("Напишите свой вопрос:")
            context.user_data['waiting_ai_question'] = True

    async def general_analysis(self, query, user_id):
        loans = await self.db.get_active_loans(user_id)
        cards = await self.db.get_active_credit_cards(user_id)

        context = {
            'debts': [dict(l) for l in loans] + [dict(c) for c in cards],
            'monthly_income': 0,
            'mandatory_expenses': 0
        }

        advice = await self.claude.get_financial_advice(context)
        await query.edit_message_text(f"💡 РЕКОМЕНДАЦИИ AI:\n\n{advice}", reply_markup=self.keyboards.back_menu("back_main"))

    async def expenses_analysis(self, query, user_id):
        await query.edit_message_text("Анализ расходов...", reply_markup=self.keyboards.back_menu("back_main"))

    async def debt_strategy(self, query, user_id):
        loans = await self.db.get_active_loans(user_id)
        debts = [{'name': l['name'], 'current_balance': l['current_balance'], 'interest_rate': l['interest_rate'], 'monthly_payment': l['monthly_payment']} for l in loans]

        strategy = await self.claude.suggest_debt_strategy(debts, 100000, 30000)
        await query.edit_message_text(f"🎯 СТРАТЕГИЯ ПОГАШЕНИЯ ДОЛГОВ:\n\n{strategy}", reply_markup=self.keyboards.back_menu("back_main"))

    async def budget_help(self, query, user_id):
        await query.edit_message_text("Помощь с бюджетом...", reply_markup=self.keyboards.back_menu("back_main"))
