"""
Управление базой данных SQLite
"""
import aiosqlite
from datetime import datetime
from config import DATABASE_PATH


class Database:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Таблица кредитов и займов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    loan_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    principal_amount REAL NOT NULL,
                    current_balance REAL NOT NULL,
                    interest_rate REAL NOT NULL,
                    monthly_payment REAL NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    payment_day INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Таблица кредитных карт
            await db.execute('''
                CREATE TABLE IF NOT EXISTS credit_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    bank_name TEXT NOT NULL,
                    card_name TEXT,
                    credit_limit REAL NOT NULL,
                    current_balance REAL NOT NULL,
                    interest_rate REAL NOT NULL,
                    grace_period_days INTEGER DEFAULT 50,
                    minimum_payment_percent REAL DEFAULT 5.0,
                    payment_day INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Таблица платежей по кредитам
            await db.execute('''
                CREATE TABLE IF NOT EXISTS loan_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    loan_id INTEGER NOT NULL,
                    payment_date DATE NOT NULL,
                    amount REAL NOT NULL,
                    principal_part REAL,
                    interest_part REAL,
                    payment_type TEXT DEFAULT 'regular',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (loan_id) REFERENCES loans(id)
                )
            ''')

            # Таблица кредитных каникул
            await db.execute('''
                CREATE TABLE IF NOT EXISTS loan_holidays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    loan_id INTEGER NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    recalculated BOOLEAN DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (loan_id) REFERENCES loans(id)
                )
            ''')

            # Таблица доходов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS incomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date DATE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Таблица расходов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    expense_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date DATE NOT NULL,
                    is_regular BOOLEAN DEFAULT 0,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Таблица бюджетов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_income REAL,
                    mandatory_expenses REAL,
                    loan_payments REAL,
                    optional_budget REAL,
                    emergency_fund_target REAL,
                    emergency_fund_current REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    UNIQUE(user_id, month, year)
                )
            ''')

            # Таблица AI-рекомендаций и решений
            await db.execute('''
                CREATE TABLE IF NOT EXISTS ai_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    decision_type TEXT NOT NULL,
                    context TEXT,
                    decision TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Таблица целей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS financial_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    goal_type TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    current_amount REAL DEFAULT 0,
                    deadline DATE,
                    is_completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Таблица категорий бюджета
            await db.execute('''
                CREATE TABLE IF NOT EXISTS budget_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    category_name TEXT NOT NULL,
                    planned_amount REAL NOT NULL,
                    spent_amount REAL DEFAULT 0,
                    category_type TEXT DEFAULT 'optional',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(month, year, category_name)
                )
            ''')

            # Таблица запланированных расходов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS planned_expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL,
                    due_date DATE NOT NULL,
                    category TEXT,
                    is_paid BOOLEAN DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Таблица истории расходов пользователей (для общего бюджета)
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_expense_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (expense_id) REFERENCES expenses(id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Таблица интеграций с банками
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bank_integrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    bank_name TEXT NOT NULL,
                    api_token TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    last_sync_date TIMESTAMP,
                    sync_enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    UNIQUE(user_id, bank_name)
                )
            ''')

            # Таблица импортированных банковских операций
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bank_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    integration_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    operation_id TEXT NOT NULL,
                    operation_date TIMESTAMP NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'RUB',
                    operation_type TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    mcc_code TEXT,
                    counterparty_name TEXT,
                    counterparty_account TEXT,
                    is_processed BOOLEAN DEFAULT 0,
                    is_ignored BOOLEAN DEFAULT 0,
                    linked_expense_id INTEGER,
                    linked_income_id INTEGER,
                    ai_classification TEXT,
                    needs_clarification BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (integration_id) REFERENCES bank_integrations(id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (linked_expense_id) REFERENCES expenses(id),
                    FOREIGN KEY (linked_income_id) REFERENCES incomes(id),
                    UNIQUE(integration_id, operation_id)
                )
            ''')

            await db.commit()

    # ===== USERS =====
    async def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Добавить пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
                (user_id, username, first_name)
            )
            await db.commit()

    async def get_user(self, user_id: int):
        """Получить пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
                return await cursor.fetchone()

    # ===== LOANS =====
    async def add_loan(self, user_id: int, loan_type: str, name: str, principal_amount: float,
                      interest_rate: float, monthly_payment: float, start_date: str,
                      payment_day: int = None, end_date: str = None):
        """Добавить кредит/займ"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO loans (user_id, loan_type, name, principal_amount, current_balance,
                                 interest_rate, monthly_payment, start_date, end_date, payment_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, loan_type, name, principal_amount, principal_amount, interest_rate,
                  monthly_payment, start_date, end_date, payment_day))
            await db.commit()
            return cursor.lastrowid

    async def get_active_loans(self, user_id: int):
        """Получить все активные кредиты пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM loans WHERE user_id = ? AND is_active = 1 ORDER BY interest_rate DESC',
                (user_id,)
            ) as cursor:
                return await cursor.fetchall()

    async def update_loan_balance(self, loan_id: int, new_balance: float):
        """Обновить текущий баланс кредита"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE loans SET current_balance = ? WHERE id = ?',
                (new_balance, loan_id)
            )
            await db.commit()

    async def close_loan(self, loan_id: int):
        """Закрыть кредит"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE loans SET is_active = 0, current_balance = 0 WHERE id = ?',
                (loan_id,)
            )
            await db.commit()

    async def update_loan(self, loan_id: int, **kwargs):
        """Обновить параметры кредита"""
        allowed_fields = {
            'name', 'current_balance', 'interest_rate', 'monthly_payment',
            'payment_day', 'end_date', 'principal_amount'
        }

        # Фильтруем только разрешенные поля
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not updates:
            return False

        # Формируем SQL запрос
        set_clause = ', '.join([f"{field} = ?" for field in updates.keys()])
        values = list(updates.values()) + [loan_id]

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f'UPDATE loans SET {set_clause} WHERE id = ?',
                values
            )
            await db.commit()
            return True

    async def delete_loan(self, loan_id: int):
        """Удалить кредит полностью (вместе со всеми платежами и каникулами)"""
        async with aiosqlite.connect(self.db_path) as db:
            # Удалить связанные платежи
            await db.execute('DELETE FROM loan_payments WHERE loan_id = ?', (loan_id,))
            # Удалить связанные каникулы
            await db.execute('DELETE FROM loan_holidays WHERE loan_id = ?', (loan_id,))
            # Удалить сам кредит
            await db.execute('DELETE FROM loans WHERE id = ?', (loan_id,))
            await db.commit()
            return True

    async def get_loan_by_name(self, user_id: int, name: str):
        """Найти кредит по названию (частичное совпадение)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM loans WHERE user_id = ? AND name LIKE ? AND is_active = 1',
                (user_id, f'%{name}%')
            ) as cursor:
                return await cursor.fetchall()

    # ===== CREDIT CARDS =====
    async def add_credit_card(self, user_id: int, bank_name: str, credit_limit: float,
                             interest_rate: float, card_name: str = None,
                             grace_period_days: int = 50, minimum_payment_percent: float = 5.0,
                             payment_day: int = None):
        """Добавить кредитную карту"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO credit_cards (user_id, bank_name, card_name, credit_limit, current_balance,
                                        interest_rate, grace_period_days, minimum_payment_percent, payment_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, bank_name, card_name, credit_limit, 0, interest_rate,
                  grace_period_days, minimum_payment_percent, payment_day))
            await db.commit()
            return cursor.lastrowid

    async def get_active_credit_cards(self, user_id: int):
        """Получить все активные кредитные карты"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM credit_cards WHERE user_id = ? AND is_active = 1',
                (user_id,)
            ) as cursor:
                return await cursor.fetchall()

    async def update_card_balance(self, card_id: int, new_balance: float):
        """Обновить баланс кредитной карты"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE credit_cards SET current_balance = ? WHERE id = ?',
                (new_balance, card_id)
            )
            await db.commit()

    async def update_credit_card(self, card_id: int, **kwargs):
        """Обновить параметры кредитной карты"""
        allowed_fields = {
            'bank_name', 'card_name', 'credit_limit', 'current_balance',
            'interest_rate', 'grace_period_days', 'minimum_payment_percent', 'payment_day'
        }

        # Фильтруем только разрешенные поля
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not updates:
            return False

        # Формируем SQL запрос
        set_clause = ', '.join([f"{field} = ?" for field in updates.keys()])
        values = list(updates.values()) + [card_id]

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f'UPDATE credit_cards SET {set_clause} WHERE id = ?',
                values
            )
            await db.commit()
            return True

    async def delete_credit_card(self, card_id: int):
        """Удалить кредитную карту полностью"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM credit_cards WHERE id = ?', (card_id,))
            await db.commit()
            return True

    async def get_card_by_bank(self, user_id: int, bank_name: str):
        """Найти кредитную карту по названию банка (частичное совпадение)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM credit_cards WHERE user_id = ? AND bank_name LIKE ? AND is_active = 1',
                (user_id, f'%{bank_name}%')
            ) as cursor:
                return await cursor.fetchall()

    # ===== LOAN PAYMENTS =====
    async def add_loan_payment(self, loan_id: int, amount: float, payment_date: str,
                              principal_part: float = None, interest_part: float = None,
                              payment_type: str = 'regular', notes: str = None):
        """Добавить платеж по кредиту"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO loan_payments (loan_id, payment_date, amount, principal_part,
                                         interest_part, payment_type, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (loan_id, payment_date, amount, principal_part, interest_part, payment_type, notes))
            await db.commit()

    # ===== INCOMES =====
    async def add_income(self, user_id: int, category: str, amount: float,
                        date: str, description: str = None):
        """Добавить доход"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO incomes (user_id, category, amount, date, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, category, amount, date, description))
            await db.commit()

    async def get_incomes(self, user_id: int, start_date: str = None, end_date: str = None):
        """Получить доходы за период"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if start_date and end_date:
                query = 'SELECT * FROM incomes WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date DESC'
                params = (user_id, start_date, end_date)
            else:
                query = 'SELECT * FROM incomes WHERE user_id = ? ORDER BY date DESC LIMIT 50'
                params = (user_id,)

            async with db.execute(query, params) as cursor:
                return await cursor.fetchall()

    # ===== EXPENSES =====
    async def add_expense(self, user_id: int, category: str, expense_type: str,
                         amount: float, date: str, is_regular: bool = False,
                         description: str = None):
        """Добавить расход"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO expenses (user_id, category, expense_type, amount, date, is_regular, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, category, expense_type, amount, date, is_regular, description))
            await db.commit()
            return cursor.lastrowid

    async def get_expenses(self, user_id: int, start_date: str = None, end_date: str = None):
        """Получить расходы за период"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if start_date and end_date:
                query = 'SELECT * FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date DESC'
                params = (user_id, start_date, end_date)
            else:
                query = 'SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT 50'
                params = (user_id,)

            async with db.execute(query, params) as cursor:
                return await cursor.fetchall()

    async def get_regular_expenses(self, user_id: int):
        """Получить регулярные расходы"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT category, AVG(amount) as avg_amount FROM expenses WHERE user_id = ? AND is_regular = 1 GROUP BY category',
                (user_id,)
            ) as cursor:
                return await cursor.fetchall()

    # ===== BUDGETS =====
    async def save_budget(self, user_id: int, month: int, year: int, **kwargs):
        """Сохранить бюджет"""
        async with aiosqlite.connect(self.db_path) as db:
            fields = ', '.join(kwargs.keys())
            placeholders = ', '.join(['?' for _ in kwargs])
            values = list(kwargs.values())

            await db.execute(f'''
                INSERT INTO budgets (user_id, month, year, {fields})
                VALUES (?, ?, ?, {placeholders})
                ON CONFLICT(user_id, month, year) DO UPDATE SET
                    {', '.join([f'{k}=excluded.{k}' for k in kwargs.keys()])},
                    updated_at=CURRENT_TIMESTAMP
            ''', (user_id, month, year, *values))
            await db.commit()

    async def get_budget(self, user_id: int, month: int, year: int):
        """Получить бюджет"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM budgets WHERE user_id = ? AND month = ? AND year = ?',
                (user_id, month, year)
            ) as cursor:
                return await cursor.fetchone()

    # ===== AI DECISIONS =====
    async def save_ai_decision(self, user_id: int, decision_type: str, decision: str, context: str = None):
        """Сохранить решение AI"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO ai_decisions (user_id, decision_type, decision, context)
                VALUES (?, ?, ?, ?)
            ''', (user_id, decision_type, decision, context))
            await db.commit()

    async def get_ai_decisions(self, user_id: int, decision_type: str = None, limit: int = 10):
        """Получить решения AI"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if decision_type:
                query = 'SELECT * FROM ai_decisions WHERE user_id = ? AND decision_type = ? ORDER BY created_at DESC LIMIT ?'
                params = (user_id, decision_type, limit)
            else:
                query = 'SELECT * FROM ai_decisions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?'
                params = (user_id, limit)

            async with db.execute(query, params) as cursor:
                return await cursor.fetchall()

    # ===== FINANCIAL GOALS =====
    async def add_financial_goal(self, user_id: int, goal_type: str, target_amount: float, deadline: str = None):
        """Добавить финансовую цель"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO financial_goals (user_id, goal_type, target_amount, deadline)
                VALUES (?, ?, ?, ?)
            ''', (user_id, goal_type, target_amount, deadline))
            await db.commit()
            return cursor.lastrowid

    async def update_goal_progress(self, goal_id: int, current_amount: float):
        """Обновить прогресс цели"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE financial_goals SET current_amount = ? WHERE id = ?',
                (current_amount, goal_id)
            )
            await db.commit()

    async def get_active_goals(self, user_id: int):
        """Получить активные цели"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM financial_goals WHERE user_id = ? AND is_completed = 0',
                (user_id,)
            ) as cursor:
                return await cursor.fetchall()

    # ===== BUDGET CATEGORIES =====
    async def add_budget_category(self, month: int, year: int, category_name: str, 
                                  planned_amount: float, category_type: str = 'optional', notes: str = None):
        """Добавить категорию бюджета"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO budget_categories (month, year, category_name, planned_amount, category_type, notes, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (month, year, category_name, planned_amount, category_type, notes))
            await db.commit()

    async def get_budget_categories(self, month: int, year: int):
        """Получить все категории бюджета за месяц"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM budget_categories WHERE month = ? AND year = ? ORDER BY category_type, category_name',
                (month, year)
            ) as cursor:
                return await cursor.fetchall()

    async def update_category_spent(self, month: int, year: int, category_name: str, amount: float):
        """Обновить потраченную сумму в категории"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE budget_categories 
                SET spent_amount = spent_amount + ?, updated_at = CURRENT_TIMESTAMP
                WHERE month = ? AND year = ? AND category_name = ?
            ''', (amount, month, year, category_name))
            await db.commit()

    async def get_category_status(self, month: int, year: int, category_name: str):
        """Получить статус категории бюджета"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM budget_categories WHERE month = ? AND year = ? AND category_name = ?',
                (month, year, category_name)
            ) as cursor:
                return await cursor.fetchone()

    # ===== PLANNED EXPENSES =====
    async def add_planned_expense(self, user_id: int, title: str, amount: float, 
                                 due_date: str, category: str = None, notes: str = None):
        """Добавить запланированный расход"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO planned_expenses (user_id, title, amount, due_date, category, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, title, amount, due_date, category, notes))
            await db.commit()
            return cursor.lastrowid

    async def get_planned_expenses(self, user_id: int = None, start_date: str = None, end_date: str = None):
        """Получить запланированные расходы"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if user_id and start_date and end_date:
                query = '''SELECT * FROM planned_expenses 
                          WHERE user_id = ? AND due_date BETWEEN ? AND ? AND is_paid = 0 
                          ORDER BY due_date'''
                params = (user_id, start_date, end_date)
            elif user_id:
                query = 'SELECT * FROM planned_expenses WHERE user_id = ? AND is_paid = 0 ORDER BY due_date'
                params = (user_id,)
            else:
                query = 'SELECT * FROM planned_expenses WHERE is_paid = 0 ORDER BY due_date'
                params = ()
            
            async with db.execute(query, params) as cursor:
                return await cursor.fetchall()

    async def mark_planned_expense_paid(self, planned_id: int):
        """Отметить запланированный расход как оплаченный"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE planned_expenses SET is_paid = 1 WHERE id = ?',
                (planned_id,)
            )
            await db.commit()

    async def get_all_users(self):
        """Получить всех пользователей"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM users') as cursor:
                return await cursor.fetchall()

    async def track_user_expense(self, expense_id: int, user_id: int, month: int, year: int):
        """Отследить какой пользователь внёс расход (для общего бюджета)"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO user_expense_tracking (expense_id, user_id, month, year)
                VALUES (?, ?, ?, ?)
            ''', (expense_id, user_id, month, year))
            await db.commit()

    async def get_user_expenses_for_month(self, user_id: int, month: int, year: int):
        """Получить расходы конкретного пользователя за месяц"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT e.* FROM expenses e
                JOIN user_expense_tracking uet ON e.id = uet.expense_id
                WHERE uet.user_id = ? AND uet.month = ? AND uet.year = ?
                ORDER BY e.date DESC
            ''', (user_id, month, year)) as cursor:
                return await cursor.fetchall()

    # ===== LOAN HOLIDAYS (КРЕДИТНЫЕ КАНИКУЛЫ) =====
    async def add_loan_holiday(self, loan_id: int, start_date: str, end_date: str, notes: str = None):
        """Добавить кредитные каникулы"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO loan_holidays (loan_id, start_date, end_date, notes)
                VALUES (?, ?, ?, ?)
            ''', (loan_id, start_date, end_date, notes))
            await db.commit()
            return cursor.lastrowid

    async def get_loan_holidays(self, loan_id: int):
        """Получить все каникулы по кредиту"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM loan_holidays WHERE loan_id = ? ORDER BY start_date',
                (loan_id,)
            ) as cursor:
                return await cursor.fetchall()

    async def mark_holiday_recalculated(self, holiday_id: int):
        """Отметить что каникулы учтены в графике"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE loan_holidays SET recalculated = 1 WHERE id = ?',
                (holiday_id,)
            )
            await db.commit()

    async def get_active_holiday_for_loan(self, loan_id: int, current_date: str):
        """Проверить активны ли каникулы для кредита на текущую дату"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM loan_holidays
                WHERE loan_id = ? AND ? BETWEEN start_date AND end_date
            ''', (loan_id, current_date)) as cursor:
                return await cursor.fetchone()

    # ===== BANK INTEGRATIONS (ИНТЕГРАЦИЯ С БАНКАМИ) =====
    async def add_bank_integration(self, user_id: int, bank_name: str, api_token: str):
        """Добавить интеграцию с банком"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT OR REPLACE INTO bank_integrations (user_id, bank_name, api_token, is_active, sync_enabled)
                VALUES (?, ?, ?, 1, 1)
            ''', (user_id, bank_name, api_token))
            await db.commit()
            return cursor.lastrowid

    async def get_user_bank_integration(self, user_id: int, bank_name: str = 'T-Bank'):
        """Получить интеграцию пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM bank_integrations WHERE user_id = ? AND bank_name = ? AND is_active = 1',
                (user_id, bank_name)
            ) as cursor:
                return await cursor.fetchone()

    async def update_integration_sync_date(self, integration_id: int):
        """Обновить дату последней синхронизации"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE bank_integrations SET last_sync_date = CURRENT_TIMESTAMP WHERE id = ?',
                (integration_id,)
            )
            await db.commit()

    async def add_bank_transaction(self, integration_id: int, user_id: int, operation_data: dict):
        """Добавить банковскую операцию"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT OR IGNORE INTO bank_transactions
                (integration_id, user_id, operation_id, operation_date, amount, currency,
                 operation_type, description, category, mcc_code, counterparty_name, counterparty_account)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                integration_id, user_id,
                operation_data['operation_id'],
                operation_data['operation_date'],
                operation_data['amount'],
                operation_data.get('currency', 'RUB'),
                operation_data['operation_type'],
                operation_data.get('description'),
                operation_data.get('category'),
                operation_data.get('mcc_code'),
                operation_data.get('counterparty_name'),
                operation_data.get('counterparty_account')
            ))
            await db.commit()
            return cursor.lastrowid

    async def get_unprocessed_transactions(self, user_id: int, limit: int = 50):
        """Получить необработанные банковские операции"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM bank_transactions
                WHERE user_id = ? AND is_processed = 0 AND is_ignored = 0
                ORDER BY operation_date DESC
                LIMIT ?
            ''', (user_id, limit)) as cursor:
                return await cursor.fetchall()

    async def mark_transaction_processed(self, transaction_id: int, expense_id: int = None, income_id: int = None):
        """Отметить транзакцию как обработанную"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE bank_transactions
                SET is_processed = 1, linked_expense_id = ?, linked_income_id = ?
                WHERE id = ?
            ''', (expense_id, income_id, transaction_id))
            await db.commit()

    async def mark_transaction_ignored(self, transaction_id: int):
        """Отметить транзакцию как игнорируемую"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE bank_transactions SET is_ignored = 1 WHERE id = ?',
                (transaction_id,)
            )
            await db.commit()

    async def check_if_internal_transfer(self, user_id: int, counterparty_account: str):
        """Проверить является ли операция переводом между пользователями бота"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            # Проверяем есть ли другой пользователь бота с такой же интеграцией
            async with db.execute('''
                SELECT u.user_id FROM users u
                JOIN bank_integrations bi ON u.user_id = bi.user_id
                WHERE u.user_id != ? AND bi.is_active = 1
            ''', (user_id,)) as cursor:
                other_users = await cursor.fetchall()
                # Это упрощенная проверка - в реальности нужно сравнивать счета
                return len(other_users) > 0

    async def delete_all_user_data(self, user_id: int):
        """
        ОПАСНО! Удалить ВСЕ данные пользователя из базы.
        Используется только при явном запросе пользователя.
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Удалить все записи связанные с пользователем
            # В порядке зависимостей (сначала зависимые таблицы)

            # Платежи по кредитам
            await db.execute('''
                DELETE FROM loan_payments
                WHERE loan_id IN (SELECT id FROM loans WHERE user_id = ?)
            ''', (user_id,))

            # Кредитные каникулы
            await db.execute('''
                DELETE FROM loan_holidays
                WHERE loan_id IN (SELECT id FROM loans WHERE user_id = ?)
            ''', (user_id,))

            # Банковские транзакции
            await db.execute('DELETE FROM bank_transactions WHERE user_id = ?', (user_id,))

            # Отслеживание расходов пользователя
            await db.execute('DELETE FROM user_expense_tracking WHERE user_id = ?', (user_id,))

            # Запланированные расходы
            await db.execute('DELETE FROM planned_expenses WHERE user_id = ?', (user_id,))

            # Категории бюджета
            await db.execute('DELETE FROM budget_categories WHERE user_id = ?', (user_id,))

            # Доходы
            await db.execute('DELETE FROM incomes WHERE user_id = ?', (user_id,))

            # Расходы
            await db.execute('DELETE FROM expenses WHERE user_id = ?', (user_id,))

            # Кредитные карты
            await db.execute('DELETE FROM credit_cards WHERE user_id = ?', (user_id,))

            # Кредиты
            await db.execute('DELETE FROM loans WHERE user_id = ?', (user_id,))

            # Банковские интеграции
            await db.execute('DELETE FROM bank_integrations WHERE user_id = ?', (user_id,))

            await db.commit()
            return True
