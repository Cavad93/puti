"""
Финансовые расчеты для кредитов и займов
"""
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class FinancialCalculator:
    """Класс для расчетов по кредитам и займам"""

    @staticmethod
    def calculate_annuity_payment(principal: float, rate: float, months: int) -> float:
        """
        Расчет аннуитетного платежа

        Args:
            principal: Сумма кредита
            rate: Годовая процентная ставка (например, 15.5)
            months: Срок кредита в месяцах

        Returns:
            Ежемесячный платеж
        """
        if rate == 0:
            return principal / months

        monthly_rate = rate / 100 / 12
        payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / \
                  ((1 + monthly_rate) ** months - 1)
        return round(payment, 2)

    @staticmethod
    def calculate_loan_schedule(principal: float, rate: float, monthly_payment: float,
                                start_date: datetime = None) -> List[Dict]:
        """
        Рассчитать график платежей по кредиту

        Args:
            principal: Текущий остаток долга
            rate: Годовая процентная ставка
            monthly_payment: Ежемесячный платеж
            start_date: Дата начала расчета

        Returns:
            Список словарей с информацией о каждом платеже
        """
        if start_date is None:
            start_date = datetime.now()

        schedule = []
        balance = principal
        monthly_rate = rate / 100 / 12
        payment_date = start_date
        payment_number = 1

        while balance > 0:
            interest = balance * monthly_rate
            principal_part = monthly_payment - interest

            if principal_part > balance:
                principal_part = balance
                monthly_payment = balance + interest

            balance -= principal_part

            schedule.append({
                'payment_number': payment_number,
                'date': payment_date.strftime('%Y-%m-%d'),
                'payment': round(monthly_payment, 2),
                'principal': round(principal_part, 2),
                'interest': round(interest, 2),
                'balance': round(max(0, balance), 2)
            })

            payment_date += relativedelta(months=1)
            payment_number += 1

            # Защита от бесконечного цикла
            if payment_number > 600:  # 50 лет
                break

        return schedule

    @staticmethod
    def calculate_early_repayment(current_balance: float, rate: float, monthly_payment: float,
                                  extra_payment: float) -> Dict:
        """
        Рассчитать эффект досрочного погашения

        Args:
            current_balance: Текущий остаток долга
            rate: Годовая процентная ставка
            monthly_payment: Ежемесячный платеж
            extra_payment: Сумма досрочного погашения

        Returns:
            Словарь с информацией об экономии
        """
        # График без досрочного погашения
        schedule_normal = FinancialCalculator.calculate_loan_schedule(
            current_balance, rate, monthly_payment
        )

        # График с досрочным погашением
        new_balance = current_balance - extra_payment
        schedule_early = FinancialCalculator.calculate_loan_schedule(
            new_balance, rate, monthly_payment
        )

        total_normal = sum(p['payment'] for p in schedule_normal)
        total_early = sum(p['payment'] for p in schedule_early) + extra_payment

        savings = total_normal - total_early
        months_saved = len(schedule_normal) - len(schedule_early)

        return {
            'new_balance': round(new_balance, 2),
            'months_saved': months_saved,
            'money_saved': round(savings, 2),
            'total_payments_before': round(total_normal, 2),
            'total_payments_after': round(total_early, 2),
            'remaining_months': len(schedule_early)
        }

    @staticmethod
    def calculate_credit_card_interest(balance: float, rate: float, days: int = 30,
                                      grace_period: bool = False) -> float:
        """
        Рассчитать проценты по кредитной карте

        Args:
            balance: Текущий баланс карты
            rate: Годовая процентная ставка
            days: Количество дней
            grace_period: Действует ли льготный период

        Returns:
            Сумма процентов
        """
        if grace_period or balance <= 0:
            return 0.0

        daily_rate = rate / 100 / 365
        interest = balance * daily_rate * days
        return round(interest, 2)

    @staticmethod
    def calculate_minimum_payment(balance: float, min_percent: float = 5.0,
                                 min_amount: float = 1000.0) -> float:
        """
        Рассчитать минимальный платеж по кредитной карте

        Args:
            balance: Текущий баланс карты
            min_percent: Минимальный процент от долга
            min_amount: Минимальная сумма платежа

        Returns:
            Минимальный платеж
        """
        if balance <= 0:
            return 0.0

        percent_payment = balance * (min_percent / 100)
        return round(max(percent_payment, min_amount), 2)

    @staticmethod
    def debt_snowball_strategy(debts: List[Dict]) -> List[Dict]:
        """
        Стратегия "Снежный ком" - погашение долгов от меньшего к большему

        Args:
            debts: Список долгов с полями: name, balance, rate, monthly_payment

        Returns:
            Отсортированный список долгов для погашения
        """
        return sorted(debts, key=lambda x: x['balance'])

    @staticmethod
    def debt_avalanche_strategy(debts: List[Dict]) -> List[Dict]:
        """
        Стратегия "Лавина" - погашение долгов с наивысшей процентной ставкой

        Args:
            debts: Список долгов с полями: name, balance, rate, monthly_payment

        Returns:
            Отсортированный список долгов для погашения
        """
        return sorted(debts, key=lambda x: x['rate'], reverse=True)

    @staticmethod
    def compare_strategies(debts: List[Dict], extra_monthly: float = 0) -> Dict:
        """
        Сравнить стратегии погашения долгов

        Args:
            debts: Список долгов
            extra_monthly: Дополнительная сумма для погашения долгов ежемесячно

        Returns:
            Сравнение стратегий
        """
        snowball_order = FinancialCalculator.debt_snowball_strategy(debts)
        avalanche_order = FinancialCalculator.debt_avalanche_strategy(debts)

        # Симуляция погашения по стратегии "Снежный ком"
        snowball_result = FinancialCalculator._simulate_debt_payoff(
            snowball_order.copy(), extra_monthly
        )

        # Симуляция погашения по стратегии "Лавина"
        avalanche_result = FinancialCalculator._simulate_debt_payoff(
            avalanche_order.copy(), extra_monthly
        )

        return {
            'snowball': {
                'order': [d['name'] for d in snowball_order],
                'total_months': snowball_result['months'],
                'total_interest': snowball_result['total_interest'],
                'total_paid': snowball_result['total_paid']
            },
            'avalanche': {
                'order': [d['name'] for d in avalanche_order],
                'total_months': avalanche_result['months'],
                'total_interest': avalanche_result['total_interest'],
                'total_paid': avalanche_result['total_paid']
            },
            'recommended': 'avalanche' if avalanche_result['total_interest'] < snowball_result['total_interest'] else 'snowball',
            'savings_with_avalanche': round(snowball_result['total_interest'] - avalanche_result['total_interest'], 2)
        }

    @staticmethod
    def _simulate_debt_payoff(debts: List[Dict], extra_monthly: float) -> Dict:
        """
        Симуляция погашения долгов

        Args:
            debts: Список долгов в порядке погашения
            extra_monthly: Дополнительная сумма

        Returns:
            Результат симуляции
        """
        total_months = 0
        total_interest = 0
        total_paid = 0
        active_debts = debts.copy()

        while active_debts:
            month_count = 0
            available_extra = extra_monthly

            for debt in active_debts[:]:
                if debt['balance'] <= 0:
                    active_debts.remove(debt)
                    continue

                monthly_rate = debt['rate'] / 100 / 12
                interest = debt['balance'] * monthly_rate
                principal = debt['monthly_payment'] - interest

                # Применяем дополнительную сумму к первому долгу
                if active_debts.index(debt) == 0 and available_extra > 0:
                    principal += available_extra
                    available_extra = 0

                debt['balance'] -= principal
                total_interest += interest
                total_paid += (principal + interest)

                if debt['balance'] <= 0:
                    debt['balance'] = 0

                month_count = 1

            if month_count > 0:
                total_months += 1

            # Защита от бесконечного цикла
            if total_months > 600:
                break

        return {
            'months': total_months,
            'total_interest': round(total_interest, 2),
            'total_paid': round(total_paid, 2)
        }

    @staticmethod
    def calculate_emergency_fund_target(monthly_mandatory_expenses: float, months: int = 6) -> float:
        """
        Рассчитать целевую сумму подушки безопасности

        Args:
            monthly_mandatory_expenses: Ежемесячные обязательные расходы
            months: Количество месяцев (обычно 3-6)

        Returns:
            Целевая сумма
        """
        return round(monthly_mandatory_expenses * months, 2)

    @staticmethod
    def calculate_months_to_payoff(balance: float, monthly_payment: float, rate: float) -> int:
        """
        Рассчитать количество месяцев до полного погашения

        Args:
            balance: Текущий остаток
            monthly_payment: Ежемесячный платеж
            rate: Годовая процентная ставка

        Returns:
            Количество месяцев
        """
        if monthly_payment <= 0:
            return 0

        monthly_rate = rate / 100 / 12

        if monthly_rate == 0:
            return int(balance / monthly_payment) + (1 if balance % monthly_payment > 0 else 0)

        # Проверка, что платеж покрывает хотя бы проценты
        min_payment = balance * monthly_rate
        if monthly_payment <= min_payment:
            return 999  # Долг не будет погашен

        months = 0
        current_balance = balance

        while current_balance > 0:
            interest = current_balance * monthly_rate
            principal = monthly_payment - interest
            current_balance -= principal
            months += 1

            if months > 600:  # Защита от бесконечного цикла
                break

        return months
