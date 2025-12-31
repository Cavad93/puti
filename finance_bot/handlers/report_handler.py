"""Обработчик генерации отчетов"""
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import calendar

class ReportHandler:
    def __init__(self, db, keyboards, reporter):
        self.db = db
        self.keyboards = keyboards
        self.reporter = reporter

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id

        if query.data == "report_expenses":
            context.user_data['report_type'] = 'expenses'
            await query.edit_message_text(
                "Выберите период для отчета по расходам:",
                reply_markup=self.keyboards.report_period_menu()
            )

        elif query.data == "report_incomes":
            context.user_data['report_type'] = 'incomes'
            await query.edit_message_text(
                "Выберите период для отчета по доходам:",
                reply_markup=self.keyboards.report_period_menu()
            )

        elif query.data == "report_debts":
            await self.generate_debt_report(query, context)

        elif query.data == "report_monthly":
            await self.generate_monthly_report(query, context)

        elif query.data == "report_forecast":
            await self.generate_forecast_report(query, context)

        elif query.data.startswith("period_"):
            await self.handle_period_selection(query, context)

    async def handle_period_selection(self, query, context):
        user_id = query.from_user.id
        period = query.data.replace("period_", "")
        report_type = context.user_data.get('report_type')

        now = datetime.now()

        if period == "current_month":
            start_date = now.replace(day=1).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        elif period == "last_month":
            last_month = now.replace(day=1) - timedelta(days=1)
            start_date = last_month.replace(day=1).strftime('%Y-%m-%d')
            end_date = last_month.replace(day=calendar.monthrange(last_month.year, last_month.month)[1]).strftime('%Y-%m-%d')
        elif period == "week":
            start_date = (now - timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        elif period == "30days":
            start_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        else:
            await query.edit_message_text("Введите даты в формате ДД.ММ.ГГГГ - ДД.ММ.ГГГГ")
            return

        await self.generate_report(query, report_type, start_date, end_date)

    async def generate_report(self, query, report_type, start_date, end_date):
        user_id = query.from_user.id

        if report_type == 'expenses':
            expenses = await self.db.get_expenses(user_id, start_date, end_date)
            text, filepath = await self.reporter.generate_expense_report([dict(e) for e in expenses], start_date, end_date)
        elif report_type == 'incomes':
            incomes = await self.db.get_incomes(user_id, start_date, end_date)
            text, filepath = await self.reporter.generate_income_report([dict(i) for i in incomes], start_date, end_date)
        else:
            text = "Неизвестный тип отчета"
            filepath = None

        await query.edit_message_text(text)
        if filepath:
            await query.message.reply_photo(photo=open(filepath, 'rb'))

    async def generate_debt_report(self, query, context):
        user_id = query.from_user.id
        loans = await self.db.get_active_loans(user_id)
        cards = await self.db.get_active_credit_cards(user_id)

        text, filepath = await self.reporter.generate_debt_report([dict(l) for l in loans], [dict(c) for c in cards])

        await query.edit_message_text(text)
        if filepath:
            await query.message.reply_photo(photo=open(filepath, 'rb'))

    async def generate_monthly_report(self, query, context):
        await query.edit_message_text("Генерация месячного отчета...")

    async def generate_forecast_report(self, query, context):
        await query.edit_message_text("Генерация прогноза погашения долгов...")
