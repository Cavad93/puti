"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ALLOWED_USER_IDS = [int(uid) for uid in os.getenv('ALLOWED_USER_IDS', '').split(',') if uid.strip()]

# Имена пользователей (для персонализации и отчетов)
USER_NAMES = {
    939056216: 'Джавад',
    497894337: 'Рустем'
}

def get_user_name(user_id: int) -> str:
    """Получить имя пользователя по ID"""
    return USER_NAMES.get(user_id, f'Пользователь {user_id}')

# Claude API
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
CLAUDE_MODEL = 'claude-haiku-4-5'  # Claude Haiku 4.5 - быстрая и дешевая модель (в 3 раза дешевле Sonnet)

# База данных
DATABASE_PATH = os.getenv('DATABASE_PATH', 'finance_bot.db')

# Часовой пояс
TIMEZONE = os.getenv('TIMEZONE', 'Europe/Moscow')

# Время напоминания (22:00 по МСК)
REMINDER_HOUR = 22
REMINDER_MINUTE = 0

# Категории расходов
EXPENSE_CATEGORIES = {
    'mandatory': {
        'Продукты': 'Еда и продукты питания',
        'Коммунальные': 'Коммунальные платежи',
        'Транспорт': 'Общественный транспорт, бензин',
        'Связь': 'Интернет, мобильная связь',
        'Аренда': 'Аренда жилья',
        'Лекарства': 'Медицина и лекарства',
    },
    'optional': {
        'Развлечения': 'Кино, рестораны, хобби',
        'Одежда': 'Одежда и обувь',
        'Образование': 'Курсы, книги',
        'Красота': 'Салоны красоты, косметика',
        'Спорт': 'Фитнес, спортинвентарь',
        'Подарки': 'Подарки',
    },
    'unplanned': {
        'Незапланированное': 'Прочие незапланированные расходы',
    }
}

# Категории доходов
INCOME_CATEGORIES = [
    'Зарплата',
    'Подработка',
    'Пассивный доход',
    'Возврат долга',
    'Подарок',
    'Другое',
]

# Типы кредитов
LOAN_TYPES = [
    'Потребительский кредит',
    'Микрозайм',
    'Кредитная карта',
]
