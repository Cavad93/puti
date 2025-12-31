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
            },
            {
                "name": "create_budget_category",
                "description": "Создать категорию бюджета на месяц. Используй когда пользователь планирует бюджет и указывает суммы на категории (продукты, ремонт, развлечения и т.д.)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "month": {"type": "integer", "description": "Месяц (1-12)"},
                        "year": {"type": "integer", "description": "Год"},
                        "category_name": {"type": "string", "description": "Название категории (Продукты, Развлечения, Ремонт машины и т.д.)"},
                        "planned_amount": {"type": "number", "description": "Запланированная сумма на категорию"},
                        "category_type": {"type": "string", "description": "Тип: mandatory (обязательные), optional (необязательные), loan (кредиты)"},
                        "notes": {"type": "string", "description": "Заметки (опционально)"}
                    },
                    "required": ["month", "year", "category_name", "planned_amount"]
                }
            },
            {
                "name": "add_planned_expense",
                "description": "Добавить запланированный будущий расход. Используй когда пользователь говорит о будущих тратах (например: 'через 5 месяцев вернуть долг Стасу', 'на день рождения сестры 23.02.2026 нужно 10000')",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Описание расхода (например, 'Вернуть долг Стасу', 'Подарок сестре на день рождения')"},
                        "amount": {"type": "number", "description": "Сумма расхода"},
                        "due_date": {"type": "string", "description": "Дата когда нужно заплатить (YYYY-MM-DD)"},
                        "category": {"type": "string", "description": "Категория расхода (опционально)"},
                        "notes": {"type": "string", "description": "Дополнительные заметки"}
                    },
                    "required": ["title", "amount", "due_date"]
                }
            },
            {
                "name": "get_budget_status",
                "description": "Получить статус бюджета за месяц - все категории с запланированными и потраченными суммами",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "month": {"type": "integer", "description": "Месяц (1-12)"},
                        "year": {"type": "integer", "description": "Год"}
                    },
                    "required": ["month", "year"]
                }
            },
            {
                "name": "get_planned_expenses",
                "description": "Получить список запланированных будущих расходов",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "description": "Начало периода (YYYY-MM-DD)"},
                        "end_date": {"type": "string", "description": "Конец периода (YYYY-MM-DD)"}
                    },
                    "required": []
                }
            },
            {
                "name": "calculate_early_payment",
                "description": "Рассчитать выгоду от досрочного погашения кредита. Показывает сколько можно сэкономить и на сколько месяцев быстрее выплатить",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "loan_identifier": {"type": "string", "description": "Название банка или ID кредита"},
                        "extra_payment": {"type": "number", "description": "Сумма досрочного погашения"}
                    },
                    "required": ["loan_identifier", "extra_payment"]
                }
            },
            {
                "name": "set_loan_holiday",
                "description": "Установить кредитные каникулы для кредита. Используй когда пользователь говорит об оформлении каникул по кредиту",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "loan_identifier": {"type": "string", "description": "Название банка или ID кредита"},
                        "start_date": {"type": "string", "description": "Дата начала каникул (YYYY-MM-DD)"},
                        "end_date": {"type": "string", "description": "Дата окончания каникул (YYYY-MM-DD)"},
                        "notes": {"type": "string", "description": "Примечания (опционально)"}
                    },
                    "required": ["loan_identifier", "start_date", "end_date"]
                }
            },
            {
                "name": "get_loan_holidays",
                "description": "Получить все кредитные каникулы пользователя (активные и будущие). ВАЖНО: используй этот инструмент ПЕРЕД любыми расчетами, прогнозами и рекомендациями по долгам!",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "connect_bank_api",
                "description": "Подключить API Т-Банка. Используй когда пользователь хочет добавить банковскую интеграцию и предоставляет API токен",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "api_token": {"type": "string", "description": "API токен от Т-Банка"}
                    },
                    "required": ["api_token"]
                }
            },
            {
                "name": "sync_bank_operations",
                "description": "Синхронизировать операции из Т-Банка. Загружает последние операции и предлагает пользователю классифицировать их",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "days": {"type": "integer", "description": "Количество дней для синхронизации (по умолчанию 7)"}
                    },
                    "required": []
                }
            },
            {
                "name": "update_loan",
                "description": "Обновить параметры существующего кредита. Используй когда пользователь хочет изменить данные кредита (сумму, ставку, платеж и т.д.)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "loan_identifier": {"type": "string", "description": "Название банка или ID кредита для поиска"},
                        "name": {"type": "string", "description": "Новое название (опционально)"},
                        "current_balance": {"type": "number", "description": "Текущий остаток долга (опционально)"},
                        "interest_rate": {"type": "number", "description": "Новая процентная ставка (опционально)"},
                        "monthly_payment": {"type": "number", "description": "Новый ежемесячный платёж (опционально)"},
                        "payment_day": {"type": "integer", "description": "Новый день платежа (опционально)"}
                    },
                    "required": ["loan_identifier"]
                }
            },
            {
                "name": "delete_loan",
                "description": "Удалить кредит из системы полностью. Используй когда пользователь хочет удалить кредит. Если найдено несколько одинаковых записей (дубликаты), удалит все автоматически.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "loan_identifier": {"type": "string", "description": "Название банка или ID кредита"},
                        "delete_all_duplicates": {"type": "boolean", "description": "Если true, удалит все найденные одинаковые кредиты. Используй когда пользователь говорит 'удали все', 'удали этот кредит полностью', 'удали дубликаты'"}
                    },
                    "required": ["loan_identifier"]
                }
            },
            {
                "name": "update_credit_card",
                "description": "Обновить параметры кредитной карты. Используй когда пользователь хочет изменить данные карты",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "bank_name": {"type": "string", "description": "Название банка для поиска карты"},
                        "current_balance": {"type": "number", "description": "Текущий долг по карте (опционально)"},
                        "credit_limit": {"type": "number", "description": "Новый кредитный лимит (опционально)"},
                        "interest_rate": {"type": "number", "description": "Новая процентная ставка (опционально)"},
                        "payment_day": {"type": "integer", "description": "Новый день платежа (опционально)"}
                    },
                    "required": ["bank_name"]
                }
            },
            {
                "name": "delete_credit_card",
                "description": "Удалить кредитную карту из системы полностью",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "bank_name": {"type": "string", "description": "Название банка"}
                    },
                    "required": ["bank_name"]
                }
            },
            {
                "name": "remove_duplicate_loans",
                "description": "Удалить дубликаты кредитов, оставив только указанное количество. Используй когда пользователь говорит о дублирующихся записях кредитов",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "loan_name": {"type": "string", "description": "Название кредита/банка для поиска дубликатов"},
                        "keep_count": {"type": "integer", "description": "Сколько записей оставить (по умолчанию 1)"}
                    },
                    "required": ["loan_name"]
                }
            },
            {
                "name": "set_savings_goal",
                "description": "Создать или обновить цель подушки безопасности. Используй когда пользователь хочет начать копить подушку безопасности",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target_months": {"type": "integer", "description": "На сколько месяцев расходов копить (обычно 3-6 месяцев)"},
                        "monthly_expenses": {"type": "number", "description": "Среднемесячные обязательные расходы"}
                    },
                    "required": ["target_months", "monthly_expenses"]
                }
            },
            {
                "name": "add_to_savings",
                "description": "Пополнить или снять деньги с подушки безопасности. Используй когда пользователь вносит деньги в подушку или снимает",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number", "description": "Сумма для пополнения (положительная) или снятия (положительная, но transaction_type='withdrawal')"},
                        "transaction_type": {"type": "string", "description": "Тип операции: deposit (пополнение) или withdrawal (снятие)"},
                        "description": {"type": "string", "description": "Описание операции (опционально)"},
                        "date": {"type": "string", "description": "Дата в формате YYYY-MM-DD (по умолчанию сегодня)"}
                    },
                    "required": ["amount", "transaction_type"]
                }
            },
            {
                "name": "get_savings_status",
                "description": "Получить статус подушки безопасности: текущий баланс, цель, прогресс. Используй когда пользователь спрашивает о подушке безопасности",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "calculate_money_distribution",
                "description": "Рассчитать умное распределение денег между подушкой безопасности и долгами. Используй когда пользователь спрашивает как распределить деньги или получил доход",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "available_money": {"type": "number", "description": "Сумма денег доступная для распределения"}
                    },
                    "required": ["available_money"]
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
            elif tool_name == "create_budget_category":
                return await self._create_budget_category(user_id, tool_input)
            elif tool_name == "add_planned_expense":
                return await self._add_planned_expense(user_id, tool_input)
            elif tool_name == "get_budget_status":
                return await self._get_budget_status(user_id, tool_input)
            elif tool_name == "get_planned_expenses":
                return await self._get_planned_expenses(user_id, tool_input)
            elif tool_name == "calculate_early_payment":
                return await self._calculate_early_payment(user_id, tool_input)
            elif tool_name == "set_loan_holiday":
                return await self._set_loan_holiday(user_id, tool_input)
            elif tool_name == "get_loan_holidays":
                return await self._get_loan_holidays(user_id)
            elif tool_name == "connect_bank_api":
                return await self._connect_bank_api(user_id, tool_input)
            elif tool_name == "sync_bank_operations":
                return await self._sync_bank_operations(user_id, tool_input)
            elif tool_name == "update_loan":
                return await self._update_loan(user_id, tool_input)
            elif tool_name == "delete_loan":
                return await self._delete_loan(user_id, tool_input)
            elif tool_name == "update_credit_card":
                return await self._update_credit_card(user_id, tool_input)
            elif tool_name == "delete_credit_card":
                return await self._delete_credit_card(user_id, tool_input)
            elif tool_name == "remove_duplicate_loans":
                return await self._remove_duplicate_loans(user_id, tool_input)
            elif tool_name == "set_savings_goal":
                return await self._set_savings_goal(user_id, tool_input)
            elif tool_name == "add_to_savings":
                return await self._add_to_savings(user_id, tool_input)
            elif tool_name == "get_savings_status":
                return await self._get_savings_status(user_id)
            elif tool_name == "calculate_money_distribution":
                return await self._calculate_money_distribution(user_id, tool_input)
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
        amount = input_data['amount']
        category = input_data['category']
        description = input_data.get('description', '')

        # Добавить расход в БД
        expense_id = await self.db.add_expense(
            user_id=user_id,
            category=category,
            expense_type=input_data['expense_type'],
            amount=amount,
            date=date,
            is_regular=input_data.get('is_regular', False),
            description=description
        )

        # Определить месяц и год из даты
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        month = date_obj.month
        year = date_obj.year

        # Автоматическая категоризация для бюджета
        budget_category = self._auto_categorize_expense(category, description)

        # Проверить существует ли бюджет на этот месяц
        budget_categories = await self.db.get_budget_categories(month, year)
        budget_warning = ""

        if budget_categories:
            # Найти соответствующую категорию бюджета
            matched_category = None
            for budget_cat in budget_categories:
                if budget_cat['category_name'].lower() == budget_category.lower():
                    matched_category = budget_cat
                    break

            if matched_category:
                # Обновить потраченную сумму (метод add'ит amount к текущей сумме)
                await self.db.update_category_spent(
                    month=month,
                    year=year,
                    category_name=matched_category['category_name'],
                    amount=amount
                )

                # Проверить превышение бюджета
                new_spent = matched_category['spent_amount'] + amount
                planned = matched_category['planned_amount']
                if new_spent > planned:
                    overspend = new_spent - planned
                    budget_warning = f"\n⚠️ ВНИМАНИЕ: Превышен бюджет категории '{matched_category['category_name']}' на {overspend:,.2f} руб.!"
                else:
                    remaining = planned - new_spent
                    percent_used = (new_spent / planned * 100) if planned > 0 else 0
                    budget_warning = f"\n💰 Бюджет '{matched_category['category_name']}': использовано {percent_used:.1f}% ({new_spent:,.2f} из {planned:,.2f} руб.)"

            # Трекинг расхода пользователя (для общего бюджета)
            await self.db.track_user_expense(
                expense_id=expense_id,
                user_id=user_id,
                month=month,
                year=year
            )

        return {
            "success": True,
            "message": f"Расход {amount:,.2f} руб. ({category}) добавлен{budget_warning}"
        }

    def _auto_categorize_expense(self, category: str, description: str) -> str:
        """
        Автоматическая категоризация расхода для бюджета
        Возвращает нормализованное название категории бюджета
        """
        text = (category + " " + description).lower()

        # Словарь ключевых слов для категорий
        category_keywords = {
            "Продукты": ["продукты", "магазин", "супермаркет", "пятёрочка", "пятерочка", "перекрёсток", "ашан", "лента", "еда", "продуктовый"],
            "Развлечения": ["развлечения", "кино", "кинотеатр", "театр", "концерт", "бар", "кафе", "ресторан", "клуб", "развлечение"],
            "Транспорт": ["транспорт", "бензин", "заправка", "такси", "метро", "автобус", "топливо", "яндекс.такси", "uber"],
            "Кофе": ["кофе", "кофейня", "старбакс", "coffee"],
            "Одежда": ["одежда", "обувь", "магазин одежды", "zara", "h&m", "uniqlo"],
            "Здоровье": ["здоровье", "аптека", "врач", "лекарства", "медицина", "больница", "клиника"],
            "Коммунальные": ["коммунальные", "жкх", "электричество", "вода", "отопление", "квартплата"],
            "Связь": ["связь", "телефон", "интернет", "мобильная связь", "мтс", "мегафон", "билайн", "теле2"],
            "Ремонт машины": ["ремонт машины", "автосервис", "сто", "ремонт авто", "автомобиль", "запчасти"],
            "Подарки": ["подарок", "подарки", "день рождения", "праздник"],
        }

        # Поиск совпадений
        for budget_cat, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return budget_cat

        # Если не найдено совпадений, вернуть исходную категорию
        return category.capitalize()

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
        from datetime import datetime

        loans = await self.db.get_active_loans(user_id)
        if not loans:
            return {"success": True, "loans": [], "message": "Нет активных кредитов"}

        loans_list = []
        current_date = datetime.now().date().strftime('%Y-%m-%d')

        for loan in loans:
            # Проверить есть ли активные каникулы
            active_holiday = await self.db.get_active_holiday_for_loan(loan['id'], current_date)

            # Получить все каникулы по этому кредиту
            all_holidays = await self.db.get_loan_holidays(loan['id'])

            loan_info = {
                "id": loan['id'],
                "name": loan['name'],
                "type": loan['loan_type'],
                "balance": loan['current_balance'],
                "rate": loan['interest_rate'],
                "monthly_payment": loan['monthly_payment'],
                "has_active_holiday": active_holiday is not None,
                "holidays": []
            }

            # Добавить информацию о каникулах
            if all_holidays:
                for holiday in all_holidays:
                    loan_info["holidays"].append({
                        "start_date": holiday['start_date'],
                        "end_date": holiday['end_date'],
                        "notes": holiday.get('notes', ''),
                        "is_active": holiday['start_date'] <= current_date <= holiday['end_date']
                    })

            loans_list.append(loan_info)

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
        from datetime import datetime

        loans = await self.db.get_active_loans(user_id)

        if not loans:
            return {"success": False, "error": "Нет активных кредитов"}

        current_date = datetime.now().date().strftime('%Y-%m-%d')

        # Проверить каникулы для каждого кредита
        debts = []
        loans_with_holidays = []

        for l in loans:
            active_holiday = await self.db.get_active_holiday_for_loan(l['id'], current_date)

            debts.append({
                'name': l['name'],
                'balance': l['current_balance'],
                'rate': l['interest_rate'],
                'monthly_payment': l['monthly_payment']
            })

            if active_holiday:
                loans_with_holidays.append({
                    'name': l['name'],
                    'start': active_holiday['start_date'],
                    'end': active_holiday['end_date']
                })

        extra_monthly = input_data.get('extra_monthly', 0)
        comparison = self.calculator.compare_strategies(debts, extra_monthly)

        # Добавить предупреждение о каникулах
        warning_message = ""
        if loans_with_holidays:
            warning_message = "\n⚠️ **ВНИМАНИЕ: АКТИВНЫЕ КАНИКУЛЫ**\n"
            for h in loans_with_holidays:
                warning_message += f"• {h['name']}: каникулы до {h['end']}\n"
            warning_message += "Расчет может не учитывать продление срока кредита!\n"

        return {
            "success": True,
            "comparison": comparison,
            "active_holidays": loans_with_holidays,
            "holidays_warning": warning_message
        }

    async def _create_budget_category(self, user_id: int, input_data: Dict) -> Dict:
        await self.db.add_budget_category(
            month=input_data['month'],
            year=input_data['year'],
            category_name=input_data['category_name'],
            planned_amount=input_data['planned_amount'],
            category_type=input_data.get('category_type', 'optional'),
            notes=input_data.get('notes')
        )
        return {
            "success": True,
            "message": f"Категория '{input_data['category_name']}' добавлена в бюджет на {input_data['month']}/{input_data['year']} с лимитом {input_data['planned_amount']:,.2f} руб."
        }

    async def _add_planned_expense(self, user_id: int, input_data: Dict) -> Dict:
        planned_id = await self.db.add_planned_expense(
            user_id=user_id,
            title=input_data['title'],
            amount=input_data['amount'],
            due_date=input_data['due_date'],
            category=input_data.get('category'),
            notes=input_data.get('notes')
        )
        return {
            "success": True,
            "planned_id": planned_id,
            "message": f"Запланирован расход '{input_data['title']}' на {input_data['amount']:,.2f} руб. к {input_data['due_date']}"
        }

    async def _get_budget_status(self, user_id: int, input_data: Dict) -> Dict:
        month = input_data['month']
        year = input_data['year']
        
        categories = await self.db.get_budget_categories(month, year)
        
        if not categories:
            return {"success": False, "message": f"Бюджет на {month}/{year} не создан"}
        
        budget_info = []
        total_planned = 0
        total_spent = 0
        
        for cat in categories:
            planned = cat['planned_amount']
            spent = cat['spent_amount']
            remaining = planned - spent
            percent_used = (spent / planned * 100) if planned > 0 else 0
            
            total_planned += planned
            total_spent += spent
            
            status = "✅" if spent <= planned else "⚠️ ПРЕВЫШЕНИЕ"
            
            budget_info.append({
                "category": cat['category_name'],
                "planned": planned,
                "spent": spent,
                "remaining": remaining,
                "percent": percent_used,
                "status": status
            })
        
        return {
            "success": True,
            "month": month,
            "year": year,
            "categories": budget_info,
            "total_planned": total_planned,
            "total_spent": total_spent,
            "total_remaining": total_planned - total_spent
        }

    async def _get_planned_expenses(self, user_id: int, input_data: Dict) -> Dict:
        planned = await self.db.get_planned_expenses(
            user_id=user_id,
            start_date=input_data.get('start_date'),
            end_date=input_data.get('end_date')
        )
        
        if not planned:
            return {"success": True, "planned_expenses": [], "message": "Нет запланированных расходов"}
        
        planned_list = [
            {
                "id": p['id'],
                "title": p['title'],
                "amount": p['amount'],
                "due_date": p['due_date'],
                "category": p['category']
            }
            for p in planned
        ]
        
        total_planned = sum(p['amount'] for p in planned)

        return {
            "success": True,
            "planned_expenses": planned_list,
            "total_amount": total_planned,
            "count": len(planned)
        }

    async def _calculate_early_payment(self, user_id: int, input_data: Dict) -> Dict:
        """Рассчитать выгоду от досрочного погашения"""
        # Найти кредит
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
                "error": f"Кредит '{input_data['loan_identifier']}' не найден"
            }

        # Рассчитать выгоду
        extra_payment = input_data['extra_payment']
        result = self.calculator.calculate_early_repayment(
            current_balance=matching_loan['current_balance'],
            rate=matching_loan['interest_rate'],
            monthly_payment=matching_loan['monthly_payment'],
            extra_payment=extra_payment
        )

        report_text = f"📊 РАСЧЕТ ДОСРОЧНОГО ПОГАШЕНИЯ\n\n"
        report_text += f"Кредит: {matching_loan['name']}\n"
        report_text += f"Текущий остаток: {matching_loan['current_balance']:,.2f} руб.\n"
        report_text += f"Досрочный платеж: {extra_payment:,.2f} руб.\n\n"
        report_text += f"РЕЗУЛЬТАТ:\n"
        report_text += f"  Новый остаток: {result['new_balance']:,.2f} руб.\n"
        report_text += f"  Экономия месяцев: {result['months_saved']} мес.\n"
        report_text += f"  Экономия денег: {result['money_saved']:,.2f} руб.\n"
        report_text += f"  Осталось платить: {result['remaining_months']} мес.\n\n"
        report_text += f"💡 Общая переплата БЕЗ досрочки: {result['total_payments_before']:,.2f} руб.\n"
        report_text += f"💡 Общая переплата С досрочкой: {result['total_payments_after']:,.2f} руб.\n"

        return {
            "success": True,
            "message": report_text,
            "calculation": result
        }

    async def _set_loan_holiday(self, user_id: int, input_data: Dict) -> Dict:
        """Установить кредитные каникулы"""
        # Найти кредит
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
                "error": f"Кредит '{input_data['loan_identifier']}' не найден"
            }

        # Добавить каникулы
        holiday_id = await self.db.add_loan_holiday(
            loan_id=matching_loan['id'],
            start_date=input_data['start_date'],
            end_date=input_data['end_date'],
            notes=input_data.get('notes')
        )

        # Пересчитать график с учетом каникул
        from datetime import datetime
        start = datetime.strptime(input_data['start_date'], '%Y-%m-%d')
        end = datetime.strptime(input_data['end_date'], '%Y-%m-%d')
        months_holiday = (end.year - start.year) * 12 + end.month - start.month

        return {
            "success": True,
            "holiday_id": holiday_id,
            "message": f"✅ Кредитные каникулы установлены для '{matching_loan['name']}'\n"
                      f"Период: {input_data['start_date']} — {input_data['end_date']}\n"
                      f"Продолжительность: {months_holiday} мес.\n\n"
                      f"⚠️ График платежей будет продлён на {months_holiday} мес.\n"
                      f"💡 Проценты продолжат начисляться во время каникул"
        }

    async def _get_loan_holidays(self, user_id: int) -> Dict:
        """Получить все кредитные каникулы пользователя"""
        from datetime import datetime

        loans = await self.db.get_active_loans(user_id)
        if not loans:
            return {
                "success": True,
                "message": "У вас нет активных кредитов",
                "holidays": []
            }

        current_date = datetime.now().date().strftime('%Y-%m-%d')
        all_holidays = []
        active_count = 0

        for loan in loans:
            holidays = await self.db.get_loan_holidays(loan['id'])

            for holiday in holidays:
                is_active = holiday['start_date'] <= current_date <= holiday['end_date']
                is_future = holiday['start_date'] > current_date

                if is_active:
                    active_count += 1

                all_holidays.append({
                    "loan_name": loan['name'],
                    "loan_id": loan['id'],
                    "start_date": holiday['start_date'],
                    "end_date": holiday['end_date'],
                    "notes": holiday.get('notes', ''),
                    "is_active": is_active,
                    "is_future": is_future,
                    "is_past": not is_active and not is_future
                })

        if not all_holidays:
            return {
                "success": True,
                "message": "📅 Нет зарегистрированных кредитных каникул",
                "holidays": []
            }

        # Формируем сообщение
        message = f"📅 **КРЕДИТНЫЕ КАНИКУЛЫ**\n\n"

        if active_count > 0:
            message += f"🟢 **Активны сейчас:** {active_count}\n\n"

        # Группируем по статусу
        active_holidays = [h for h in all_holidays if h['is_active']]
        future_holidays = [h for h in all_holidays if h['is_future']]
        past_holidays = [h for h in all_holidays if h['is_past']]

        if active_holidays:
            message += "**🟢 АКТИВНЫЕ:**\n"
            for h in active_holidays:
                message += f"• {h['loan_name']}: {h['start_date']} — {h['end_date']}\n"
            message += "\n"

        if future_holidays:
            message += "**🔵 БУДУЩИЕ:**\n"
            for h in future_holidays:
                message += f"• {h['loan_name']}: {h['start_date']} — {h['end_date']}\n"
            message += "\n"

        if past_holidays:
            message += "**⚪ ПРОШЕДШИЕ:**\n"
            for h in past_holidays:
                message += f"• {h['loan_name']}: {h['start_date']} — {h['end_date']}\n"

        return {
            "success": True,
            "message": message,
            "holidays": all_holidays,
            "active_count": active_count,
            "total_count": len(all_holidays)
        }

    async def _connect_bank_api(self, user_id: int, input_data: Dict) -> Dict:
        """Подключить API Т-Банка"""
        api_token = input_data['api_token']

        # Сохранить интеграцию
        integration_id = await self.db.add_bank_integration(
            user_id=user_id,
            bank_name='T-Bank',
            api_token=api_token
        )

        return {
            "success": True,
            "integration_id": integration_id,
            "message": f"✅ API Т-Банка успешно подключён!\n\n"
                      f"Теперь можете использовать команду для синхронизации операций.\n"
                      f"Напишите: 'Синхронизируй операции за последнюю неделю'"
        }

    async def _sync_bank_operations(self, user_id: int, input_data: Dict) -> Dict:
        """Синхронизировать операции из Т-Банка"""
        from tbank_api import TBankAPI

        # Получить интеграцию
        integration = await self.db.get_user_bank_integration(user_id, 'T-Bank')

        if not integration:
            return {
                "success": False,
                "error": "❌ API Т-Банка не подключён.\n\nСначала подключите API: 'Подключи API Т-Банка <токен>'"
            }

        # Создать клиент
        api_client = TBankAPI(integration['api_token'])

        # Синхронизировать
        days = input_data.get('days', 7)
        operations = await api_client.sync_recent_operations(days)

        if not operations:
            return {
                "success": True,
                "message": f"ℹ️ Нет новых операций за последние {days} дней"
            }

        # Импортировать операции
        imported_count = 0
        for op in operations:
            parsed = api_client.parse_operation(op)

            # Проверить не является ли это внутренним переводом
            if parsed.get('counterparty_account'):
                is_internal = await self.db.check_if_internal_transfer(
                    user_id,
                    parsed['counterparty_account']
                )
                if is_internal:
                    continue  # Игнорировать переводы между пользователями бота

            await self.db.add_bank_transaction(
                integration_id=integration['id'],
                user_id=user_id,
                operation_data=parsed
            )
            imported_count += 1

        # Обновить дату синхронизации
        await self.db.update_integration_sync_date(integration['id'])

        # Получить необработанные операции для показа пользователю
        unprocessed = await self.db.get_unprocessed_transactions(user_id, limit=5)

        message = f"✅ Синхронизировано {imported_count} операций из Т-Банка\n\n"

        if unprocessed:
            message += f"📋 Необработанные операции (показаны первые 5):\n\n"
            for idx, tx in enumerate(unprocessed, 1):
                op_type = "➕ Доход" if tx['operation_type'] == 'income' else "➖ Расход"
                message += f"{idx}. {op_type} {tx['amount']:,.2f} руб.\n"
                message += f"   {tx['description']}\n"
                message += f"   Дата: {tx['operation_date'][:10]}\n\n"

            message += "\n💡 Скажите как классифицировать каждую операцию\n"
            message += "Например: 'Первая операция - это продукты' или 'Вторую игнорируй'"

        return {
            "success": True,
            "message": message,
            "imported_count": imported_count,
            "unprocessed_count": len(unprocessed)
        }

    async def _update_loan(self, user_id: int, input_data: Dict) -> Dict:
        """Обновить кредит"""
        loan_identifier = input_data.get('loan_identifier', '')

        # Найти кредит
        loans = await self.db.get_loan_by_name(user_id, loan_identifier)

        if not loans:
            return {
                "success": False,
                "error": f"Кредит '{loan_identifier}' не найден"
            }

        if len(loans) > 1:
            loan_list = "\n".join([f"- {loan['name']} (остаток: {loan['current_balance']:,.0f} руб)" for loan in loans])
            return {
                "success": False,
                "error": f"Найдено несколько кредитов. Уточните:\n{loan_list}"
            }

        loan = loans[0]
        loan_id = loan['id']

        # Собрать параметры для обновления
        updates = {}
        if 'name' in input_data:
            updates['name'] = input_data['name']
        if 'current_balance' in input_data:
            updates['current_balance'] = input_data['current_balance']
        if 'interest_rate' in input_data:
            updates['interest_rate'] = input_data['interest_rate']
        if 'monthly_payment' in input_data:
            updates['monthly_payment'] = input_data['monthly_payment']
        if 'payment_day' in input_data:
            updates['payment_day'] = input_data['payment_day']

        if not updates:
            return {
                "success": False,
                "error": "Не указано ни одного параметра для обновления"
            }

        # Обновить
        success = await self.db.update_loan(loan_id, **updates)

        if success:
            updated_fields = ", ".join(updates.keys())
            return {
                "success": True,
                "message": f"✅ Кредит '{loan['name']}' обновлен (изменены поля: {updated_fields})"
            }
        else:
            return {
                "success": False,
                "error": "Не удалось обновить кредит"
            }

    async def _delete_loan(self, user_id: int, input_data: Dict) -> Dict:
        """Удалить кредит"""
        loan_identifier = input_data.get('loan_identifier', '')
        delete_all = input_data.get('delete_all_duplicates', False)

        # Найти кредит
        loans = await self.db.get_loan_by_name(user_id, loan_identifier)

        if not loans:
            return {
                "success": False,
                "error": f"Кредит '{loan_identifier}' не найден"
            }

        # Если несколько кредитов
        if len(loans) > 1:
            # Проверить все ли идентичные (дубликаты)
            first_loan = loans[0]
            all_identical = all(
                loan['name'] == first_loan['name'] and
                loan['current_balance'] == first_loan['current_balance'] and
                loan['interest_rate'] == first_loan['interest_rate'] and
                loan['monthly_payment'] == first_loan['monthly_payment']
                for loan in loans
            )

            # Если все идентичные или пользователь явно попросил удалить все
            if all_identical or delete_all:
                # Удалить все кредиты
                deleted_count = 0
                for loan in loans:
                    success = await self.db.delete_loan(loan['id'])
                    if success:
                        deleted_count += 1

                return {
                    "success": True,
                    "message": f"✅ Удалено {deleted_count} записей кредита '{first_loan['name']}' (дубликаты)"
                }
            else:
                # Разные кредиты - попросить уточнить
                loan_list = "\n".join([f"- {loan['name']} (остаток: {loan['current_balance']:,.0f} руб)" for loan in loans])
                return {
                    "success": False,
                    "error": f"Найдено несколько разных кредитов. Уточните какой удалить:\n{loan_list}"
                }

        # Один кредит - удалить
        loan = loans[0]
        loan_name = loan['name']

        # Удалить
        success = await self.db.delete_loan(loan['id'])

        if success:
            return {
                "success": True,
                "message": f"✅ Кредит '{loan_name}' удалён из системы"
            }
        else:
            return {
                "success": False,
                "error": "Не удалось удалить кредит"
            }

    async def _update_credit_card(self, user_id: int, input_data: Dict) -> Dict:
        """Обновить кредитную карту"""
        bank_name = input_data.get('bank_name', '')

        # Найти карту
        cards = await self.db.get_card_by_bank(user_id, bank_name)

        if not cards:
            return {
                "success": False,
                "error": f"Кредитная карта '{bank_name}' не найдена"
            }

        if len(cards) > 1:
            card_list = "\n".join([f"- {card['bank_name']} (долг: {card['current_balance']:,.0f} руб)" for card in cards])
            return {
                "success": False,
                "error": f"Найдено несколько карт. Уточните:\n{card_list}"
            }

        card = cards[0]
        card_id = card['id']

        # Собрать параметры для обновления
        updates = {}
        if 'current_balance' in input_data:
            updates['current_balance'] = input_data['current_balance']
        if 'credit_limit' in input_data:
            updates['credit_limit'] = input_data['credit_limit']
        if 'interest_rate' in input_data:
            updates['interest_rate'] = input_data['interest_rate']
        if 'payment_day' in input_data:
            updates['payment_day'] = input_data['payment_day']

        if not updates:
            return {
                "success": False,
                "error": "Не указано ни одного параметра для обновления"
            }

        # Обновить
        success = await self.db.update_credit_card(card_id, **updates)

        if success:
            updated_fields = ", ".join(updates.keys())
            return {
                "success": True,
                "message": f"✅ Кредитная карта '{card['bank_name']}' обновлена (изменены поля: {updated_fields})"
            }
        else:
            return {
                "success": False,
                "error": "Не удалось обновить карту"
            }

    async def _delete_credit_card(self, user_id: int, input_data: Dict) -> Dict:
        """Удалить кредитную карту"""
        bank_name = input_data.get('bank_name', '')

        # Найти карту
        cards = await self.db.get_card_by_bank(user_id, bank_name)

        if not cards:
            return {
                "success": False,
                "error": f"Кредитная карта '{bank_name}' не найдена"
            }

        if len(cards) > 1:
            card_list = "\n".join([f"- {card['bank_name']} (долг: {card['current_balance']:,.0f} руб)" for card in cards])
            return {
                "success": False,
                "error": f"Найдено несколько карт. Уточните:\n{card_list}"
            }

        card = cards[0]
        card_name = card['bank_name']

        # Удалить
        success = await self.db.delete_credit_card(card['id'])

        if success:
            return {
                "success": True,
                "message": f"✅ Кредитная карта '{card_name}' удалена из системы"
            }
        else:
            return {
                "success": False,
                "error": "Не удалось удалить карту"
            }

    async def _remove_duplicate_loans(self, user_id: int, input_data: Dict) -> Dict:
        """Удалить дубликаты кредитов"""
        loan_name = input_data.get('loan_name', '')
        keep_count = input_data.get('keep_count', 1)

        if not loan_name:
            return {
                "success": False,
                "error": "Не указано название кредита"
            }

        # Сначала проверим сколько всего кредитов с таким названием
        loans = await self.db.get_loan_by_name(user_id, loan_name)

        if not loans:
            return {
                "success": False,
                "error": f"Кредиты с названием '{loan_name}' не найдены"
            }

        if len(loans) <= keep_count:
            return {
                "success": False,
                "error": f"Найдено всего {len(loans)} кредит(ов) '{loan_name}', дубликатов нет"
            }

        # Удалить дубликаты
        deleted_count = await self.db.find_and_delete_duplicate_loans(
            user_id,
            loan_name,
            keep_count
        )

        if deleted_count > 0:
            return {
                "success": True,
                "message": f"✅ Удалено {deleted_count} дубликат(ов) кредита '{loan_name}'. Осталась {keep_count} запись(ей)."
            }
        else:
            return {
                "success": False,
                "error": "Не удалось удалить дубликаты"
            }

    # ===== EMERGENCY FUND / SAVINGS (ПОДУШКА БЕЗОПАСНОСТИ) =====

    async def _set_savings_goal(self, user_id: int, input_data: Dict) -> Dict:
        """Создать цель подушки безопасности"""
        target_months = input_data['target_months']
        monthly_expenses = input_data['monthly_expenses']

        # Создать цель
        goal_id = await self.db.add_savings_goal(user_id, target_months, monthly_expenses)

        target_amount = target_months * monthly_expenses

        return {
            "success": True,
            "message": f"✅ Создана цель подушки безопасности!\n\n"
                      f"🎯 Цель: {target_amount:,.0f} руб. ({target_months} мес. × {monthly_expenses:,.0f} руб.)\n"
                      f"📊 Текущий баланс: 0 руб.\n"
                      f"💪 Начинайте копить! Система будет помогать распределять деньги оптимально."
        }

    async def _add_to_savings(self, user_id: int, input_data: Dict) -> Dict:
        """Пополнить или снять деньги с подушки безопасности"""
        amount = input_data['amount']
        transaction_type = input_data['transaction_type']
        description = input_data.get('description', '')
        date = input_data.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Получить активную цель
        goal = await self.db.get_active_savings_goal(user_id)

        if not goal:
            return {
                "success": False,
                "error": "❌ У вас нет активной цели подушки безопасности. Сначала создайте цель командой 'Хочу копить подушку безопасности'."
            }

        # Добавить транзакцию
        await self.db.add_to_savings(
            user_id=user_id,
            goal_id=goal['id'],
            amount=amount,
            date=date,
            transaction_type=transaction_type,
            description=description
        )

        # Получить обновленные данные
        updated_goal = await self.db.get_active_savings_goal(user_id)
        current_amount = updated_goal['current_amount']
        target_amount = updated_goal['target_amount']
        progress_percent = (current_amount / target_amount * 100) if target_amount > 0 else 0
        months_covered = await self.db.calculate_months_covered(user_id)

        if transaction_type == 'deposit':
            emoji = "💰"
            action = "Пополнение"
        else:
            emoji = "📤"
            action = "Снятие"

        return {
            "success": True,
            "message": f"{emoji} {action} подушки безопасности: {amount:,.0f} руб.\n\n"
                      f"📊 Текущий баланс: {current_amount:,.0f} руб.\n"
                      f"🎯 Цель: {target_amount:,.0f} руб.\n"
                      f"📈 Прогресс: {progress_percent:.1f}%\n"
                      f"🛡️ Покрытие: {months_covered:.1f} мес. расходов"
        }

    async def _get_savings_status(self, user_id: int) -> Dict:
        """Получить статус подушки безопасности"""
        # Получить активную цель
        goal = await self.db.get_active_savings_goal(user_id)

        if not goal:
            return {
                "success": True,
                "message": "💡 У вас пока нет подушки безопасности.\n\n"
                          "Подушка безопасности - это деньги на 3-6 месяцев обязательных расходов. "
                          "Она защищает от потери работы, болезни или других непредвиденных ситуаций.\n\n"
                          "Хотите начать копить? Скажите мне сколько у вас обязательных расходов в месяц."
            }

        current_amount = goal['current_amount']
        target_amount = goal['target_amount']
        target_months = goal['target_months']
        monthly_expenses = goal['monthly_expenses']
        progress_percent = (current_amount / target_amount * 100) if target_amount > 0 else 0
        months_covered = await self.db.calculate_months_covered(user_id)

        # Определить статус
        if months_covered < 1:
            status_emoji = "⚠️"
            status_text = "КРИТИЧНО"
            advice = "У вас нет даже месяца на жизнь! Начните копить срочно."
        elif months_covered < 3:
            status_emoji = "⏳"
            status_text = "МАЛО"
            advice = "Продолжайте копить до 3 месяцев минимум."
        elif months_covered >= target_months:
            status_emoji = "✅"
            status_text = "ЦЕЛЬ ДОСТИГНУТА!"
            advice = "Отличная работа! Можете сфокусироваться на погашении долгов."
        else:
            status_emoji = "💪"
            status_text = "В ПРОЦЕССЕ"
            advice = f"Осталось накопить {target_amount - current_amount:,.0f} руб. до цели."

        # Получить историю
        history = await self.db.get_savings_history(user_id, limit=5)
        history_text = ""
        if history:
            history_text = "\n\n📜 Последние операции:\n"
            for h in history:
                date_str = h['date']
                amount = h['amount']
                trans_type = h['transaction_type']
                emoji_t = "➕" if trans_type == 'deposit' else "➖"
                history_text += f"  {emoji_t} {date_str}: {amount:,.0f} руб.\n"

        return {
            "success": True,
            "message": f"{status_emoji} СТАТУС ПОДУШКИ БЕЗОПАСНОСТИ: {status_text}\n\n"
                      f"💰 Текущий баланс: {current_amount:,.0f} руб.\n"
                      f"🎯 Цель: {target_amount:,.0f} руб. ({target_months} мес.)\n"
                      f"📈 Прогресс: {progress_percent:.1f}%\n"
                      f"🛡️ Покрытие: {months_covered:.1f} мес. расходов\n"
                      f"💡 {advice}{history_text}"
        }

    async def _calculate_money_distribution(self, user_id: int, input_data: Dict) -> Dict:
        """Рассчитать умное распределение денег между подушкой и долгами"""
        available_money = input_data['available_money']

        # Получить данные подушки безопасности
        savings = await self.db.get_savings_balance(user_id)

        if not savings:
            return {
                "success": False,
                "error": "❌ Сначала создайте цель подушки безопасности. Скажите мне сколько у вас обязательных расходов в месяц."
            }

        emergency_fund_current = savings['current_amount']
        emergency_fund_target = savings['target_amount']
        monthly_expenses = savings['monthly_expenses']

        # Получить список долгов
        loans = await self.db.get_active_loans(user_id)
        cards = await self.db.get_active_credit_cards(user_id)

        debts = []
        for loan in loans:
            debts.append({
                'name': loan['name'],
                'balance': loan['current_balance'],
                'rate': loan['interest_rate'],
                'monthly_payment': loan['monthly_payment']
            })

        for card in cards:
            if card['current_balance'] > 0:
                debts.append({
                    'name': f"Карта {card['bank_name']}",
                    'balance': card['current_balance'],
                    'rate': card['interest_rate'],
                    'monthly_payment': self.calculator.calculate_minimum_payment(card['current_balance'])
                })

        if not debts:
            # Нет долгов - все деньги на подушку
            return {
                "success": True,
                "message": f"💰 Распределение {available_money:,.0f} руб.:\n\n"
                          f"✅ У вас нет долгов! Все деньги идут в подушку безопасности:\n"
                          f"  💰 На подушку: {available_money:,.0f} руб.\n\n"
                          f"После этого у вас будет: {emergency_fund_current + available_money:,.0f} руб."
            }

        # Рассчитать распределение
        distribution = self.calculator.calculate_money_distribution(
            available_money=available_money,
            emergency_fund_current=emergency_fund_current,
            emergency_fund_target=emergency_fund_target,
            monthly_expenses=monthly_expenses,
            debts=debts
        )

        # Сформировать сообщение
        message = f"💰 УМНОЕ РАСПРЕДЕЛЕНИЕ {available_money:,.0f} РУБ.\n\n"
        message += f"{distribution['reason']}\n\n"
        message += f"📊 РЕКОМЕНДУЕМОЕ РАСПРЕДЕЛЕНИЕ:\n"
        message += f"  💰 На подушку: {distribution['to_emergency_fund']:,.0f} руб.\n"
        message += f"  💳 На долги: {distribution['to_debts']:,.0f} руб.\n\n"

        if distribution['debt_distribution']:
            message += f"📋 ДОЛГИ (в порядке приоритета):\n"
            for debt in distribution['debt_distribution']:
                message += f"  • {debt['name']} ({debt['rate']:.1f}%): {debt['amount']:,.0f} руб.\n"
                message += f"    Останется: {debt['remaining_balance']:,.0f} руб.\n"

        message += f"\n🛡️ ПОДУШКА БЕЗОПАСНОСТИ:\n"
        message += f"  Было: {distribution['emergency_fund_before']:,.0f} руб. ({distribution['months_covered_before']:.1f} мес.)\n"
        message += f"  Станет: {distribution['emergency_fund_after']:,.0f} руб. ({distribution['months_covered_after']:.1f} мес.)\n"
        message += f"  До цели: {distribution['still_need_for_target']:,.0f} руб.\n"

        return {
            "success": True,
            "message": message
        }
