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

    @staticmethod
    def calculate_money_distribution(
        available_money: float,
        emergency_fund_current: float,
        emergency_fund_target: float,
        monthly_expenses: float,
        debts: List[Dict]
    ) -> Dict:
        """
        Умный расчет распределения денег между подушкой безопасности и долгами

        Args:
            available_money: Доступная сумма для распределения
            emergency_fund_current: Текущий размер подушки безопасности
            emergency_fund_target: Целевая сумма подушки безопасности
            monthly_expenses: Месячные обязательные расходы
            debts: Список долгов с полями: name, balance, rate, monthly_payment

        Returns:
            Словарь с рекомендациями по распределению
        """
        # Рассчитать на сколько месяцев хватит текущей подушки
        months_covered = emergency_fund_current / monthly_expenses if monthly_expenses > 0 else 0

        # Найти высокопроцентные долги (>25%)
        high_interest_debts = [d for d in debts if d['rate'] > 25]
        total_high_interest_debt = sum(d['balance'] for d in high_interest_debts)

        # Определить стратегию распределения
        strategy = ""
        to_emergency_fund = 0
        to_debts = 0
        debt_distribution = []

        if months_covered < 1:
            # Критическая ситуация - нет даже месяца
            # 50% на подушку, 50% на долги
            strategy = "critical"
            to_emergency_fund = available_money * 0.5
            to_debts = available_money * 0.5
            reason = "❗ У вас нет подушки безопасности даже на 1 месяц. Это критично!"

        elif months_covered >= 1 and months_covered < 3 and high_interest_debts:
            # Есть 1-3 месяца, но есть грабительские кредиты
            # 20% на подушку, 80% на высокопроцентные долги
            strategy = "balanced_aggressive"
            to_emergency_fund = available_money * 0.2
            to_debts = available_money * 0.8
            reason = f"✅ У вас есть подушка на {months_covered:.1f} мес. Но есть кредиты под >25%! Давайте их закроем!"

        elif months_covered >= 3:
            # Есть минимум 3 месяца - можно сфокусироваться на долгах
            # 10% на подушку (для поддержания), 90% на долги
            strategy = "debt_focused"
            to_emergency_fund = available_money * 0.1
            to_debts = available_money * 0.9
            reason = f"🎯 У вас отличная подушка на {months_covered:.1f} мес! Фокус на погашение долгов!"

        else:
            # Есть 1-3 месяца, но нет грабительских кредитов
            # 30% на подушку, 70% на долги
            strategy = "balanced"
            to_emergency_fund = available_money * 0.3
            to_debts = available_money * 0.7
            reason = f"💪 У вас {months_covered:.1f} мес подушки. Наращиваем до 3 месяцев + гасим долги."

        # Распределить деньги по долгам (стратегия "Лавина" - сначала высокопроцентные)
        if to_debts > 0 and debts:
            sorted_debts = sorted(debts, key=lambda x: x['rate'], reverse=True)
            remaining_money = to_debts

            for debt in sorted_debts:
                if remaining_money <= 0:
                    break

                # Сколько выделить на этот долг
                allocation = min(remaining_money, debt['balance'])
                debt_distribution.append({
                    'name': debt['name'],
                    'amount': round(allocation, 2),
                    'rate': debt['rate'],
                    'remaining_balance': round(debt['balance'] - allocation, 2)
                })
                remaining_money -= allocation

        # Рассчитать новый баланс подушки после пополнения
        new_emergency_fund = emergency_fund_current + to_emergency_fund
        new_months_covered = new_emergency_fund / monthly_expenses if monthly_expenses > 0 else 0
        progress_percent = (new_emergency_fund / emergency_fund_target * 100) if emergency_fund_target > 0 else 0

        return {
            'strategy': strategy,
            'reason': reason,
            'to_emergency_fund': round(to_emergency_fund, 2),
            'to_debts': round(to_debts, 2),
            'debt_distribution': debt_distribution,
            'emergency_fund_before': round(emergency_fund_current, 2),
            'emergency_fund_after': round(new_emergency_fund, 2),
            'months_covered_before': round(months_covered, 2),
            'months_covered_after': round(new_months_covered, 2),
            'target_progress_percent': round(progress_percent, 2),
            'still_need_for_target': round(max(0, emergency_fund_target - new_emergency_fund), 2)
        }
