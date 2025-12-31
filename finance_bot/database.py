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
            await db.execute('''
                INSERT INTO expenses (user_id, category, expense_type, amount, date, is_regular, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, category, expense_type, amount, date, is_regular, description))
            await db.commit()

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
