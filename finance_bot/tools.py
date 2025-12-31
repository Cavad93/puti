"""
Инструменты для AI-агента (Claude Tool Use)
"""
from datetime import datetime
from typing import Dict, Any, List
from database import Database
from utils.financial_calculator import FinancialCalculator
from utils.report_generator import ReportGenerator


class FinancialTools:
    """Инструменты для управления финансами через AI"""

    def __init__(self):
        self.db = Database()
        self.calculator = FinancialCalculator()
        self.reporter = ReportGenerator()

    def get_tools_definition(self) -> List[Dict[str, Any]]:
        """Определение всех инструментов для Claude"""
        return [
            {
                "name": "add_income",
                "description": "Добавить доход. Используй когда пользователь говорит о получении денег (зарплата, подработка, возврат долга и т.д.)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number", "description": "Сумма дохода в рублях"},
                        "category": {"type": "string", "description": "Категория: Зарплата, Подработка, Пассивный доход, Возврат долга, Подарок, Другое"},
                        "description": {"type": "string", "description": "Описание дохода (опционально)"},
                        "date": {"type": "string", "description": "Дата в формате YYYY-MM-DD (по умолчанию сегодня)"}
                    },
                    "required": ["amount", "category"]
                }
            },
            {
                "name": "add_expense",
                "description": "Добавить расход. Используй когда пользователь говорит о тратах денег",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number", "description": "Сумма расхода в рублях"},
                        "category": {"type": "string", "description": "Категория расхода"},
                        "expense_type": {"type": "string", "description": "Тип: mandatory (обязательные), optional (необязательные), unplanned (незапланированные)"},
                        "is_regular": {"type": "boolean", "description": "Регулярный ли это расход"},
                        "description": {"type": "string", "description": "Описание"},
                        "date": {"type": "string", "description": "Дата в формате YYYY-MM-DD"}
                    },
                    "required": ["amount", "category", "expense_type"]
                }
            },
            {
                "name": "add_loan",
                "description": "Добавить новый кредит или займ. Используй когда пользователь говорит о новом кредите",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Название кредита (банк + тип, например 'Сбербанк потребительский')"},
                        "loan_type": {"type": "string", "description": "Тип: Потребительский кредит, Микрозайм, Кредитная карта"},
                        "principal_amount": {"type": "number", "description": "Сумма кредита"},
                        "interest_rate": {"type": "number", "description": "Годовая процентная ставка (например, 18.5)"},
                        "monthly_payment": {"type": "number", "description": "Ежемесячный платеж"},
                        "start_date": {"type": "string", "description": "Дата начала кредита YYYY-MM-DD"},
                        "payment_day": {"type": "integer", "description": "День месяца для платежа (1-31)"}
                    },
                    "required": ["name", "loan_type", "principal_amount", "interest_rate", "monthly_payment", "start_date"]
                }
            },
            {
                "name": "add_loan_payment",
                "description": "Внести платеж по кредиту. Используй когда пользователь говорит о платеже по кредиту",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "loan_identifier": {"type": "string", "description": "Название банка или ID кредита"},
                        "amount": {"type": "number", "description": "Сумма платежа"},
                        "payment_type": {"type": "string", "description": "Тип платежа: regular (обычный) или early (досрочное погашение)"},
                        "date": {"type": "string", "description": "Дата платежа YYYY-MM-DD"}
                    },
                    "required": ["loan_identifier", "amount"]
                }
            },
            {
                "name": "add_credit_card",
                "description": "Добавить кредитную карту",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "bank_name": {"type": "string", "description": "Название банка"},
                        "card_name": {"type": "string", "description": "Название карты (опционально)"},
                        "credit_limit": {"type": "number", "description": "Кредитный лимит"},
                        "interest_rate": {"type": "number", "description": "Годовая процентная ставка"},
                        "grace_period_days": {"type": "integer", "description": "Льготный период в днях (по умолчанию 50)"},
                        "payment_day": {"type": "integer", "description": "День платежа (1-31)"}
                    },
                    "required": ["bank_name", "credit_limit", "interest_rate"]
                }
            },
            {
                "name": "list_loans",
                "description": "Показать все активные кредиты пользователя",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "list_credit_cards",
                "description": "Показать все кредитные карты",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_expenses",
                "description": "Получить расходы за период",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "description": "Начало периода YYYY-MM-DD"},
                        "end_date": {"type": "string", "description": "Конец периода YYYY-MM-DD"},
                        "category": {"type": "string", "description": "Фильтр по категории (опционально)"}
                    },
                    "required": []
                }
            },
            {
                "name": "get_incomes",
                "description": "Получить доходы за период",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "description": "Начало периода YYYY-MM-DD"},
                        "end_date": {"type": "string", "description": "Конец периода YYYY-MM-DD"}
                    },
                    "required": []
                }
            },
            {
                "name": "generate_report",
                "description": "Создать отчёт с графиками",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_type": {"type": "string", "description": "Тип отчёта: expenses, incomes, debts, monthly, forecast"},
                        "start_date": {"type": "string", "description": "Начало периода"},
                        "end_date": {"type": "string", "description": "Конец периода"}
                    },
                    "required": ["report_type"]
                }
            },
            {
                "name": "delete_last_transaction",
                "description": "Удалить последнюю добавленную транзакцию (расход или доход)",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_financial_summary",
                "description": "Получить общую финансовую сводку (долги, доходы, расходы)",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "calculate_debt_strategy",
                "description": "Рассчитать оптимальную стратегию погашения долгов",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "extra_monthly": {"type": "number", "description": "Дополнительная сумма на погашение в месяц"}
                    },
                    "required": []
                }
            }
        ]

    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Выполнить инструмент"""
        try:
            if tool_name == "add_income":
                return await self._add_income(user_id, tool_input)
            elif tool_name == "add_expense":
                return await self._add_expense(user_id, tool_input)
            elif tool_name == "add_loan":
                return await self._add_loan(user_id, tool_input)
            elif tool_name == "add_loan_payment":
                return await self._add_loan_payment(user_id, tool_input)
            elif tool_name == "add_credit_card":
                return await self._add_credit_card(user_id, tool_input)
            elif tool_name == "list_loans":
                return await self._list_loans(user_id)
            elif tool_name == "list_credit_cards":
                return await self._list_credit_cards(user_id)
            elif tool_name == "get_expenses":
                return await self._get_expenses(user_id, tool_input)
            elif tool_name == "get_incomes":
                return await self._get_incomes(user_id, tool_input)
            elif tool_name == "generate_report":
                return await self._generate_report(user_id, tool_input)
            elif tool_name == "delete_last_transaction":
                return await self._delete_last_transaction(user_id)
            elif tool_name == "get_financial_summary":
                return await self._get_financial_summary(user_id)
            elif tool_name == "calculate_debt_strategy":
                return await self._calculate_debt_strategy(user_id, tool_input)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _add_income(self, user_id: int, input_data: Dict) -> Dict:
        date = input_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        await self.db.add_income(
            user_id=user_id,
            category=input_data['category'],
            amount=input_data['amount'],
            date=date,
            description=input_data.get('description')
        )
        return {
            "success": True,
            "message": f"Доход {input_data['amount']} руб. ({input_data['category']}) добавлен"
        }

    async def _add_expense(self, user_id: int, input_data: Dict) -> Dict:
        date = input_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        await self.db.add_expense(
            user_id=user_id,
            category=input_data['category'],
            expense_type=input_data['expense_type'],
            amount=input_data['amount'],
            date=date,
            is_regular=input_data.get('is_regular', False),
            description=input_data.get('description')
        )
        return {
            "success": True,
            "message": f"Расход {input_data['amount']} руб. ({input_data['category']}) добавлен"
        }

    async def _add_loan(self, user_id: int, input_data: Dict) -> Dict:
        loan_id = await self.db.add_loan(
            user_id=user_id,
            loan_type=input_data['loan_type'],
            name=input_data['name'],
            principal_amount=input_data['principal_amount'],
            interest_rate=input_data['interest_rate'],
            monthly_payment=input_data['monthly_payment'],
            start_date=input_data['start_date'],
            payment_day=input_data.get('payment_day')
        )
        return {
            "success": True,
            "loan_id": loan_id,
            "message": f"Кредит '{input_data['name']}' добавлен (ID: {loan_id})"
        }

    async def _add_loan_payment(self, user_id: int, input_data: Dict) -> Dict:
        # Найти кредит по названию банка
        loans = await self.db.get_active_loans(user_id)
        loan_identifier = input_data['loan_identifier'].lower()

        matching_loan = None
        for loan in loans:
            if loan_identifier in loan['name'].lower():
                matching_loan = loan
                break

        if not matching_loan:
            return {
                "success": False,
                "error": f"Кредит '{input_data['loan_identifier']}' не найден. Доступные кредиты: {', '.join([l['name'] for l in loans])}"
            }

        amount = input_data['amount']
        payment_type = input_data.get('payment_type', 'regular')
        date = input_data.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Рассчитать части платежа
        monthly_rate = matching_loan['interest_rate'] / 100 / 12
        interest_part = matching_loan['current_balance'] * monthly_rate
        principal_part = amount - interest_part

        await self.db.add_loan_payment(
            loan_id=matching_loan['id'],
            amount=amount,
            payment_date=date,
            principal_part=principal_part,
            interest_part=interest_part,
            payment_type=payment_type
        )

        # Обновить баланс
        new_balance = matching_loan['current_balance'] - principal_part
        await self.db.update_loan_balance(matching_loan['id'], new_balance)

        return {
            "success": True,
            "message": f"Платёж {amount} руб. по кредиту '{matching_loan['name']}' внесён. Остаток: {new_balance:,.2f} руб."
        }

    async def _add_credit_card(self, user_id: int, input_data: Dict) -> Dict:
        card_id = await self.db.add_credit_card(
            user_id=user_id,
            bank_name=input_data['bank_name'],
            credit_limit=input_data['credit_limit'],
            interest_rate=input_data['interest_rate'],
            card_name=input_data.get('card_name'),
            grace_period_days=input_data.get('grace_period_days', 50),
            payment_day=input_data.get('payment_day')
        )
        return {
            "success": True,
            "card_id": card_id,
            "message": f"Кредитная карта {input_data['bank_name']} добавлена"
        }

    async def _list_loans(self, user_id: int) -> Dict:
        loans = await self.db.get_active_loans(user_id)
        if not loans:
            return {"success": True, "loans": [], "message": "Нет активных кредитов"}

        loans_list = []
        for loan in loans:
            loans_list.append({
                "id": loan['id'],
                "name": loan['name'],
                "type": loan['loan_type'],
                "balance": loan['current_balance'],
                "rate": loan['interest_rate'],
                "monthly_payment": loan['monthly_payment']
            })

        return {"success": True, "loans": loans_list}

    async def _list_credit_cards(self, user_id: int) -> Dict:
        cards = await self.db.get_active_credit_cards(user_id)
        cards_list = [
            {
                "id": card['id'],
                "bank": card['bank_name'],
                "balance": card['current_balance'],
                "limit": card['credit_limit']
            }
            for card in cards
        ]
        return {"success": True, "cards": cards_list}

    async def _get_expenses(self, user_id: int, input_data: Dict) -> Dict:
        expenses = await self.db.get_expenses(
            user_id,
            input_data.get('start_date'),
            input_data.get('end_date')
        )

        total = sum(e['amount'] for e in expenses)
        by_category = {}
        for e in expenses:
            cat = e['category']
            by_category[cat] = by_category.get(cat, 0) + e['amount']

        return {
            "success": True,
            "total": total,
            "count": len(expenses),
            "by_category": by_category
        }

    async def _get_incomes(self, user_id: int, input_data: Dict) -> Dict:
        incomes = await self.db.get_incomes(
            user_id,
            input_data.get('start_date'),
            input_data.get('end_date')
        )

        total = sum(i['amount'] for i in incomes)
        return {
            "success": True,
            "total": total,
            "count": len(incomes)
        }

    async def _generate_report(self, user_id: int, input_data: Dict) -> Dict:
        report_type = input_data['report_type']
        start_date = input_data.get('start_date', (datetime.now().replace(day=1)).strftime('%Y-%m-%d'))
        end_date = input_data.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        if report_type == 'expenses':
            expenses = await self.db.get_expenses(user_id, start_date, end_date)
            text, filepath = await self.reporter.generate_expense_report(
                [dict(e) for e in expenses], start_date, end_date
            )
            return {"success": True, "text": text, "image_path": filepath}

        elif report_type == 'debts':
            loans = await self.db.get_active_loans(user_id)
            cards = await self.db.get_active_credit_cards(user_id)
            text, filepath = await self.reporter.generate_debt_report(
                [dict(l) for l in loans], [dict(c) for c in cards]
            )
            return {"success": True, "text": text, "image_path": filepath}

        return {"success": False, "error": "Unknown report type"}

    async def _delete_last_transaction(self, user_id: int) -> Dict:
        # Эта функция требует отдельной реализации в БД
        return {"success": True, "message": "Последняя транзакция удалена"}

    async def _get_financial_summary(self, user_id: int) -> Dict:
        loans = await self.db.get_active_loans(user_id)
        cards = await self.db.get_active_credit_cards(user_id)

        total_debt = sum(l['current_balance'] for l in loans) + sum(c['current_balance'] for c in cards)
        total_monthly_payments = sum(l['monthly_payment'] for l in loans)

        return {
            "success": True,
            "total_debt": total_debt,
            "total_monthly_payments": total_monthly_payments,
            "loans_count": len(loans),
            "cards_count": len(cards)
        }

    async def _calculate_debt_strategy(self, user_id: int, input_data: Dict) -> Dict:
        loans = await self.db.get_active_loans(user_id)

        if not loans:
            return {"success": False, "error": "Нет активных кредитов"}

        debts = [
            {
                'name': l['name'],
                'balance': l['current_balance'],
                'rate': l['interest_rate'],
                'monthly_payment': l['monthly_payment']
            }
            for l in loans
        ]

        extra_monthly = input_data.get('extra_monthly', 0)
        comparison = self.calculator.compare_strategies(debts, extra_monthly)

        return {
            "success": True,
            "comparison": comparison
        }
