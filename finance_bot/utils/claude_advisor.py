"""
Интеграция с Claude API для финансовых советов
"""
import anthropic
from typing import Dict, List, Optional
from datetime import datetime
from config import CLAUDE_API_KEY, CLAUDE_MODEL


class ClaudeAdvisor:
    """Финансовый советник на базе Claude"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        self.model = CLAUDE_MODEL

    async def get_financial_advice(self, user_context: Dict, question: str = None) -> str:
        """
        Получить финансовый совет от Claude

        Args:
            user_context: Контекст пользователя (долги, доходы, расходы, цели)
            question: Конкретный вопрос пользователя

        Returns:
            Совет от Claude
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(user_context, question)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            return f"Ошибка при получении совета: {str(e)}"

    async def analyze_spending(self, expenses: List[Dict], budget: Dict) -> str:
        """
        Анализ расходов и соответствия бюджету

        Args:
            expenses: Список расходов за период
            budget: Текущий бюджет

        Returns:
            Анализ и рекомендации
        """
        system_prompt = """Ты строгий финансовый советник, который помогает людям выйти из долгов.
        Твоя задача - анализировать расходы и давать конкретные рекомендации по оптимизации.
        Будь строгим, но конструктивным. Указывай на проблемные области и предлагай решения."""

        # Группировка расходов по категориям
        expense_by_category = {}
        for expense in expenses:
            category = expense.get('category', 'Без категории')
            amount = expense.get('amount', 0)
            expense_by_category[category] = expense_by_category.get(category, 0) + amount

        user_prompt = f"""
Проанализируй расходы пользователя за текущий период:

РАСХОДЫ ПО КАТЕГОРИЯМ:
{self._format_dict(expense_by_category)}

БЮДЖЕТ:
- Общий доход: {budget.get('total_income', 0)} руб.
- Обязательные расходы: {budget.get('mandatory_expenses', 0)} руб.
- Платежи по кредитам: {budget.get('loan_payments', 0)} руб.
- Бюджет на необязательное: {budget.get('optional_budget', 0)} руб.

Дай анализ:
1. Какие категории превышают разумные нормы?
2. Где можно сэкономить?
3. Конкретные рекомендации по сокращению расходов
4. Что делать дальше?

Будь строгим, но мотивирующим. Цель - помочь выбраться из долгов.
"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            return f"Ошибка при анализе расходов: {str(e)}"

    async def suggest_debt_strategy(self, debts: List[Dict], monthly_income: float,
                                   mandatory_expenses: float) -> str:
        """
        Предложить стратегию погашения долгов

        Args:
            debts: Список долгов
            monthly_income: Ежемесячный доход
            mandatory_expenses: Обязательные расходы

        Returns:
            Стратегия погашения долгов
        """
        system_prompt = """Ты эксперт по управлению долгами. Твоя задача - помочь человеку
        разработать оптимальную стратегию погашения долгов с учетом его финансовой ситуации.
        Используй методы "снежный ком" и "лавина", давай конкретные цифры и план действий."""

        debt_info = []
        for debt in debts:
            debt_info.append(
                f"- {debt.get('name', 'Без названия')}: "
                f"{debt.get('current_balance', 0)} руб., "
                f"ставка {debt.get('interest_rate', 0)}%, "
                f"платеж {debt.get('monthly_payment', 0)} руб/мес"
            )

        free_money = monthly_income - mandatory_expenses - sum(d.get('monthly_payment', 0) for d in debts)

        user_prompt = f"""
ФИНАНСОВАЯ СИТУАЦИЯ:
- Ежемесячный доход: {monthly_income} руб.
- Обязательные расходы: {mandatory_expenses} руб.
- Свободных денег после всех платежей: {free_money} руб.

ДОЛГИ:
{chr(10).join(debt_info)}

Разработай стратегию погашения долгов:
1. Какой метод использовать - "снежный ком" или "лавину"?
2. В каком порядке гасить долги?
3. Сколько дополнительно вносить на досрочное погашение?
4. Через сколько месяцев человек будет свободен от долгов?
5. Какие действия предпринять прямо сейчас?

Дай конкретный, пошаговый план.
"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            return f"Ошибка при создании стратегии: {str(e)}"

    async def create_monthly_budget(self, income: float, mandatory_expenses: float,
                                   loan_payments: float, previous_decisions: List[str] = None) -> str:
        """
        Создать месячный бюджет с учетом предыдущих решений AI

        Args:
            income: Доход
            mandatory_expenses: Обязательные расходы
            loan_payments: Платежи по кредитам
            previous_decisions: Предыдущие решения AI

        Returns:
            Бюджет с рекомендациями
        """
        system_prompt = """Ты персональный финансовый планировщик. Создавай бюджеты,
        учитывая предыдущие решения и особенности клиента. Помни о главных целях:
        погасить долги и накопить подушку безопасности."""

        context = ""
        if previous_decisions:
            context = f"\nПРЕДЫДУЩИЕ РЕШЕНИЯ И КОНТЕКСТ:\n" + "\n".join(previous_decisions[-5:])

        remaining = income - mandatory_expenses - loan_payments

        user_prompt = f"""
ДАННЫЕ ДЛЯ БЮДЖЕТА:
- Доход: {income} руб.
- Обязательные расходы: {mandatory_expenses} руб.
- Платежи по кредитам: {loan_payments} руб.
- Остается: {remaining} руб.
{context}

Создай детальный бюджет на месяц:
1. Распределение свободных денег (на досрочное погашение, подушку безопасности, необязательные расходы)
2. Конкретные цифры для каждой категории
3. Приоритеты на этот месяц
4. Правила, которых нужно придерживаться

Учти предыдущие решения и не противоречь им, если ситуация не изменилась.
"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1800,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            return f"Ошибка при создании бюджета: {str(e)}"

    async def budget_exceeded_warning(self, category: str, spent: float, budget: float,
                                     remaining_days: int) -> str:
        """
        Предупреждение о превышении бюджета

        Args:
            category: Категория расходов
            spent: Потрачено
            budget: Бюджет
            remaining_days: Осталось дней до конца месяца

        Returns:
            Строгое предупреждение
        """
        system_prompt = """Ты очень строгий финансовый наставник. Когда пользователь превышает бюджет,
        ты должен строго, но конструктивно указать на проблему и дать конкретные действия для исправления ситуации.
        Не будь грубым, но будь настойчивым и серьезным."""

        overspent = spent - budget
        percent_over = (overspent / budget * 100) if budget > 0 else 0

        user_prompt = f"""
ТРЕВОГА! Превышение бюджета в категории "{category}":
- Бюджет: {budget} руб.
- Потрачено: {spent} руб.
- Превышение: {overspent} руб. ({percent_over:.1f}%)
- До конца месяца: {remaining_days} дней

Дай строгую, но мотивирующую обратную связь:
1. Насколько это серьезно?
2. Что делать ПРЯМО СЕЙЧАС?
3. Как избежать этого в будущем?

Помни: у пользователя долги, и каждый рубль на счету!
"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            return f"Ошибка: {str(e)}"

    def _build_system_prompt(self) -> str:
        """Построить системный промпт для Claude"""
        return """Ты опытный финансовый советник, специализирующийся на помощи людям в выходе из долгов.

Твои принципы:
1. Быть честным и прямым - не обнадеживать ложными надеждами
2. Давать конкретные, действенные советы с цифрами и планами
3. Помнить, что главные цели клиента: погасить долги и создать подушку безопасности
4. Учитывать психологию - мотивировать, но быть реалистичным
5. Предлагать методы оптимизации расходов, основанные на данных
6. Всегда думать о долгосрочной финансовой свободе клиента

Говори на русском языке, используй понятные термины."""

    def _build_user_prompt(self, context: Dict, question: Optional[str]) -> str:
        """Построить промпт пользователя с контекстом"""
        prompt_parts = ["ФИНАНСОВАЯ СИТУАЦИЯ ПОЛЬЗОВАТЕЛЯ:\n"]

        # Долги
        if context.get('debts'):
            prompt_parts.append("ДОЛГИ:")
            for debt in context['debts']:
                prompt_parts.append(
                    f"- {debt.get('name')}: {debt.get('current_balance')} руб., "
                    f"ставка {debt.get('interest_rate')}%, платеж {debt.get('monthly_payment')} руб/мес"
                )
            prompt_parts.append("")

        # Доходы и расходы
        if context.get('monthly_income'):
            prompt_parts.append(f"Ежемесячный доход: {context['monthly_income']} руб.")

        if context.get('mandatory_expenses'):
            prompt_parts.append(f"Обязательные расходы: {context['mandatory_expenses']} руб.")

        # Цели
        if context.get('goals'):
            prompt_parts.append("\nЦЕЛИ:")
            for goal in context['goals']:
                prompt_parts.append(
                    f"- {goal.get('goal_type')}: {goal.get('current_amount')}/{goal.get('target_amount')} руб."
                )

        # Вопрос пользователя
        if question:
            prompt_parts.append(f"\nВОПРОС: {question}")
        else:
            prompt_parts.append("\nДай общий анализ ситуации и рекомендации на ближайший месяц.")

        return "\n".join(prompt_parts)

    def _format_dict(self, data: Dict) -> str:
        """Форматировать словарь для вывода"""
        return "\n".join([f"- {k}: {v} руб." for k, v in data.items()])
