"""
Генерация отчетов с таблицами и графиками
"""
import matplotlib
matplotlib.use('Agg')  # Для работы без GUI
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import io
import os


class ReportGenerator:
    """Генератор финансовых отчетов"""

    def __init__(self, reports_dir='finance_bot/reports'):
        self.reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)

        # Настройка matplotlib для поддержки русского языка
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False

    async def generate_expense_report(self, expenses: List[Dict], start_date: str,
                                     end_date: str) -> Tuple[str, str]:
        """
        Генерация отчета по расходам

        Args:
            expenses: Список расходов
            start_date: Начало периода
            end_date: Конец периода

        Returns:
            Tuple (текстовый отчет, путь к файлу с графиком)
        """
        if not expenses:
            return "Нет данных за выбранный период", None

        # Группировка по категориям
        df = pd.DataFrame(expenses)
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)

        # Текстовый отчет
        report_text = f"📊 ОТЧЕТ ПО РАСХОДАМ\n"
        report_text += f"Период: {start_date} — {end_date}\n\n"
        report_text += f"Общая сумма: {df['amount'].sum():,.2f} руб.\n\n"
        report_text += "ПО КАТЕГОРИЯМ:\n"

        for category, amount in category_totals.items():
            percent = (amount / df['amount'].sum()) * 100
            report_text += f"  {category}: {amount:,.2f} руб. ({percent:.1f}%)\n"

        # График
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Круговая диаграмма
        colors = plt.cm.Set3(range(len(category_totals)))
        ax1.pie(category_totals.values, labels=category_totals.index, autopct='%1.1f%%',
                colors=colors, startangle=90)
        ax1.set_title('Расходы по категориям', fontsize=14, weight='bold')

        # Столбчатая диаграмма
        ax2.bar(range(len(category_totals)), category_totals.values, color=colors)
        ax2.set_xticks(range(len(category_totals)))
        ax2.set_xticklabels(category_totals.index, rotation=45, ha='right')
        ax2.set_ylabel('Сумма (руб.)', fontsize=12)
        ax2.set_title('Сравнение расходов', fontsize=14, weight='bold')
        ax2.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        # Сохранение
        filename = f"expense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.reports_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return report_text, filepath

    async def generate_income_report(self, incomes: List[Dict], start_date: str,
                                    end_date: str) -> Tuple[str, str]:
        """
        Генерация отчета по доходам

        Args:
            incomes: Список доходов
            start_date: Начало периода
            end_date: Конец периода

        Returns:
            Tuple (текстовый отчет, путь к файлу с графиком)
        """
        if not incomes:
            return "Нет данных за выбранный период", None

        df = pd.DataFrame(incomes)
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)

        # Текстовый отчет
        report_text = f"💰 ОТЧЕТ ПО ДОХОДАМ\n"
        report_text += f"Период: {start_date} — {end_date}\n\n"
        report_text += f"Общая сумма: {df['amount'].sum():,.2f} руб.\n\n"
        report_text += "ПО ИСТОЧНИКАМ:\n"

        for category, amount in category_totals.items():
            percent = (amount / df['amount'].sum()) * 100
            report_text += f"  {category}: {amount:,.2f} руб. ({percent:.1f}%)\n"

        # График
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.Greens(range(50, 200, int(150 / len(category_totals))))

        bars = ax.barh(category_totals.index, category_totals.values, color=colors)
        ax.set_xlabel('Сумма (руб.)', fontsize=12)
        ax.set_title('Источники доходов', fontsize=14, weight='bold')
        ax.grid(axis='x', alpha=0.3)

        # Добавление значений на столбцы
        for i, (bar, value) in enumerate(zip(bars, category_totals.values)):
            ax.text(value, i, f' {value:,.0f}', va='center', fontsize=10)

        plt.tight_layout()

        filename = f"income_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.reports_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return report_text, filepath

    async def generate_debt_report(self, loans: List[Dict], credit_cards: List[Dict]) -> Tuple[str, str]:
        """
        Генерация отчета по долгам

        Args:
            loans: Список кредитов/займов
            credit_cards: Список кредитных карт

        Returns:
            Tuple (текстовый отчет, путь к файлу с графиком)
        """
        report_text = "💳 ОТЧЕТ ПО ДОЛГАМ\n\n"

        total_debt = 0
        total_monthly = 0
        debt_data = []

        if loans:
            report_text += "КРЕДИТЫ И ЗАЙМЫ:\n"
            for loan in loans:
                balance = loan.get('current_balance', 0)
                payment = loan.get('monthly_payment', 0)
                rate = loan.get('interest_rate', 0)
                total_debt += balance
                total_monthly += payment

                report_text += f"  • {loan.get('name', 'Без названия')}\n"
                report_text += f"    Остаток: {balance:,.2f} руб.\n"
                report_text += f"    Ставка: {rate}%\n"
                report_text += f"    Платеж: {payment:,.2f} руб/мес\n\n"

                debt_data.append({
                    'name': loan.get('name', 'Кредит'),
                    'balance': balance,
                    'rate': rate
                })

        if credit_cards:
            report_text += "КРЕДИТНЫЕ КАРТЫ:\n"
            for card in credit_cards:
                balance = card.get('current_balance', 0)
                limit = card.get('credit_limit', 0)
                rate = card.get('interest_rate', 0)
                total_debt += balance

                utilization = (balance / limit * 100) if limit > 0 else 0

                report_text += f"  • {card.get('bank_name', 'Банк')} {card.get('card_name', '')}\n"
                report_text += f"    Долг: {balance:,.2f} / {limit:,.2f} руб. ({utilization:.1f}%)\n"
                report_text += f"    Ставка: {rate}%\n\n"

                debt_data.append({
                    'name': f"{card.get('bank_name', 'Карта')}",
                    'balance': balance,
                    'rate': rate
                })

        report_text += f"ИТОГО:\n"
        report_text += f"  Общий долг: {total_debt:,.2f} руб.\n"
        report_text += f"  Ежемесячные платежи: {total_monthly:,.2f} руб.\n"

        if not debt_data:
            return report_text, None

        # График
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # График по размеру долга
        names = [d['name'] for d in debt_data]
        balances = [d['balance'] for d in debt_data]
        rates = [d['rate'] for d in debt_data]

        colors = plt.cm.Reds(range(50, 250, int(200 / len(debt_data))))

        ax1.barh(names, balances, color=colors)
        ax1.set_xlabel('Сумма долга (руб.)', fontsize=12)
        ax1.set_title('Долги по размеру', fontsize=14, weight='bold')
        ax1.grid(axis='x', alpha=0.3)

        # График по процентной ставке
        ax2.barh(names, rates, color=colors)
        ax2.set_xlabel('Процентная ставка (%)', fontsize=12)
        ax2.set_title('Процентные ставки', fontsize=14, weight='bold')
        ax2.grid(axis='x', alpha=0.3)

        plt.tight_layout()

        filename = f"debt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.reports_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return report_text, filepath

    async def generate_monthly_summary(self, month: int, year: int, data: Dict) -> Tuple[str, str]:
        """
        Генерация месячного сводного отчета

        Args:
            month: Месяц
            year: Год
            data: Данные (доходы, расходы, долги, бюджет)

        Returns:
            Tuple (текстовый отчет, путь к файлу с графиком)
        """
        month_names = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                      'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

        report_text = f"📈 СВОДНЫЙ ОТЧЕТ\n"
        report_text += f"{month_names[month]} {year}\n\n"

        total_income = data.get('total_income', 0)
        total_expense = data.get('total_expense', 0)
        loan_payments = data.get('loan_payments', 0)
        balance = total_income - total_expense - loan_payments

        report_text += f"💰 Доходы: {total_income:,.2f} руб.\n"
        report_text += f"📊 Расходы: {total_expense:,.2f} руб.\n"
        report_text += f"💳 Платежи по кредитам: {loan_payments:,.2f} руб.\n"
        report_text += f"{'➕' if balance >= 0 else '➖'} Баланс: {balance:,.2f} руб.\n\n"

        if 'budget' in data:
            budget = data['budget']
            report_text += "БЮДЖЕТ:\n"
            report_text += f"  Обязательные расходы: {budget.get('mandatory_expenses', 0):,.2f} руб.\n"
            report_text += f"  Бюджет на необязательное: {budget.get('optional_budget', 0):,.2f} руб.\n"
            report_text += f"  Цель - подушка безопасности: {budget.get('emergency_fund_current', 0):,.2f} / "
            report_text += f"{budget.get('emergency_fund_target', 0):,.2f} руб.\n"

        # График
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Доходы vs Расходы
        categories = ['Доходы', 'Расходы', 'Кредиты']
        values = [total_income, total_expense, loan_payments]
        colors_bar = ['#4CAF50', '#FF9800', '#F44336']

        bars = ax1.bar(categories, values, color=colors_bar, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Сумма (руб.)', fontsize=12)
        ax1.set_title('Доходы и расходы', fontsize=14, weight='bold')
        ax1.grid(axis='y', alpha=0.3)

        # Добавление значений на столбцы
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}',
                    ha='center', va='bottom', fontsize=10)

        # Распределение расходов
        if 'expense_by_type' in data:
            expense_types = data['expense_by_type']
            if expense_types:
                labels = list(expense_types.keys())
                sizes = list(expense_types.values())
                colors_pie = plt.cm.Set3(range(len(labels)))

                ax2.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors_pie, startangle=90)
                ax2.set_title('Структура расходов', fontsize=14, weight='bold')
        else:
            ax2.text(0.5, 0.5, 'Нет данных', ha='center', va='center', fontsize=14)
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)

        plt.tight_layout()

        filename = f"monthly_summary_{year}_{month:02d}_{datetime.now().strftime('%H%M%S')}.png"
        filepath = os.path.join(self.reports_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return report_text, filepath

    async def generate_debt_payoff_forecast(self, debts: List[Dict], extra_monthly: float = 0) -> Tuple[str, str]:
        """
        Прогноз погашения долгов

        Args:
            debts: Список долгов
            extra_monthly: Дополнительная сумма на погашение

        Returns:
            Tuple (текстовый отчет, путь к файлу с графиком)
        """
        from utils.financial_calculator import FinancialCalculator

        calc = FinancialCalculator()

        report_text = "🎯 ПРОГНОЗ ПОГАШЕНИЯ ДОЛГОВ\n\n"

        if extra_monthly > 0:
            report_text += f"Дополнительный платеж: {extra_monthly:,.2f} руб/мес\n\n"

        # Сравнение стратегий
        comparison = calc.compare_strategies(debts, extra_monthly)

        report_text += "СТРАТЕГИЯ 'СНЕЖНЫЙ КОМ':\n"
        report_text += f"  Порядок: {' → '.join(comparison['snowball']['order'])}\n"
        report_text += f"  Срок: {comparison['snowball']['total_months']} мес.\n"
        report_text += f"  Проценты: {comparison['snowball']['total_interest']:,.2f} руб.\n\n"

        report_text += "СТРАТЕГИЯ 'ЛАВИНА':\n"
        report_text += f"  Порядок: {' → '.join(comparison['avalanche']['order'])}\n"
        report_text += f"  Срок: {comparison['avalanche']['total_months']} мес.\n"
        report_text += f"  Проценты: {comparison['avalanche']['total_interest']:,.2f} руб.\n\n"

        report_text += f"💡 Рекомендуется: {comparison['recommended'].upper()}\n"
        report_text += f"💰 Экономия при стратегии 'Лавина': {comparison['savings_with_avalanche']:,.2f} руб.\n"

        # График сравнения
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        strategies = ['Снежный ком', 'Лавина']
        months = [comparison['snowball']['total_months'], comparison['avalanche']['total_months']]
        interest = [comparison['snowball']['total_interest'], comparison['avalanche']['total_interest']]

        # Срок погашения
        colors = ['#FF9800', '#4CAF50']
        bars1 = ax1.bar(strategies, months, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Месяцев', fontsize=12)
        ax1.set_title('Срок погашения долгов', fontsize=14, weight='bold')
        ax1.grid(axis='y', alpha=0.3)

        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)} мес',
                    ha='center', va='bottom', fontsize=10)

        # Переплата
        bars2 = ax2.bar(strategies, interest, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_ylabel('Рубли', fontsize=12)
        ax2.set_title('Переплата по процентам', fontsize=14, weight='bold')
        ax2.grid(axis='y', alpha=0.3)

        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}',
                    ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        filename = f"debt_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.reports_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return report_text, filepath
