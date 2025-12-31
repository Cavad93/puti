"""
Финансовый Telegram бот с AI-агентом
Управление через естественный диалог
"""
import logging
from datetime import time as datetime_time
import pytz

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, ALLOWED_USER_IDS, TIMEZONE, REMINDER_HOUR, REMINDER_MINUTE
from database import Database
from ai_agent import FinancialAIAgent

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class FinanceBot:
    """Финансовый бот с AI-агентом"""

    def __init__(self):
        self.db = Database()
        self.ai_agent = FinancialAIAgent()

    def check_access(self, user_id: int) -> bool:
        """Проверка доступа пользователя"""
        if not ALLOWED_USER_IDS:
            logger.warning("ALLOWED_USER_IDS не настроен!")
            return False
        return user_id in ALLOWED_USER_IDS

    async def start(self, update: Update, context):
        """Команда /start или просто 'начать'"""
        user = update.effective_user

        if not self.check_access(user.id):
            await update.message.reply_text(
                "⛔ У вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id}\n"
                "Обратитесь к администратору."
            )
            return

        # Добавить пользователя в БД
        await self.db.add_user(user.id, user.username, user.first_name)

        # Инициализировать отслеживание обновлений остатков
        update_status = await self.db.get_debt_update_status(user.id)
        if not update_status:
            await self.db.init_debt_balance_tracking(user.id)

        welcome_text = f"""Привет, {user.first_name}! 👋

Я твой AI-помощник для управления финансами. Просто пиши мне как обычному человеку:

📝 Примеры:
• "35000 на кредит в Сбере"
• "590 за кофе"
• "Получил зарплату 85000"
• "У меня кредит в Альфе 300к под 16%"
• "Сколько я потратил на кофе?"
• "Покажи мои долги"
• "Это ошибка, удали"

Я понимаю естественный язык и помогу:
✅ Вести учёт доходов и расходов
✅ Управлять кредитами
✅ Планировать бюджет
✅ Выбраться из долгов
✅ Накопить подушку безопасности

Пиши всё как есть, я пойму! 💪"""

        await update.message.reply_text(welcome_text)

    async def help_command(self, update: Update, context):
        """Команда /help или 'помощь'"""
        help_text = """📚 КАК ПОЛЬЗОВАТЬСЯ БОТОМ

Просто пиши мне обычными фразами:

💰 ДОХОДЫ:
"Зарплата 85000"
"Получил подработку 15000"
"Вернули долг 5000"

📊 РАСХОДЫ:
"590 за кофе"
"2500 на продукты"
"Купил одежду за 8000"

💳 КРЕДИТЫ:
"У меня кредит в Сбере 500к под 18%"
"Ежемесячный платёж 15000"
"35000 на кредит в Альфе"

📈 ОТЧЁТЫ:
"Покажи расходы за месяц"
"Сколько я потратил на кофе?"
"Какие у меня долги?"
"Когда расплачусь с кредитами?"

✏️ РЕДАКТИРОВАНИЕ:
"Измени сумму в Почта Банке на 1455000"
"Обнови ставку по кредиту в Сбере"
"Удали кредит в Альфе"

🔧 СПЕЦИАЛЬНЫЕ КОМАНДЫ:
• "очистить" - очистить историю диалога (данные НЕ удаляются!)
• "удалить всё" - ПОЛНОСТЬЮ удалить все данные (с подтверждением)

Я всё понимаю и помогаю! 🤖"""

        await update.message.reply_text(help_text)

    async def clear_history(self, update: Update, context):
        """Очистить историю разговора (НЕ удаляет данные!)"""
        user_id = update.effective_user.id
        self.ai_agent.clear_history(user_id)
        await update.message.reply_text(
            "🗑️ **История диалога очищена**\n\n"
            "✅ Все ваши данные сохранены:\n"
            "• Кредиты\n"
            "• Расходы и доходы\n"
            "• Платежи\n"
            "• Бюджеты\n\n"
            "Очищена только память последних сообщений для AI.",
            parse_mode="Markdown"
        )

    async def request_delete_all_data(self, update: Update, context):
        """Запрос на удаление всех данных (первый шаг)"""
        user_id = update.effective_user.id

        # Установить флаг ожидания подтверждения
        if 'user_data' not in context.bot_data:
            context.bot_data['user_data'] = {}
        context.bot_data['user_data'][user_id] = {'awaiting_delete_confirmation': True}

        await update.message.reply_text(
            "⚠️ **ВНИМАНИЕ! ОПАСНАЯ ОПЕРАЦИЯ!** ⚠️\n\n"
            "Вы собираетесь **БЕЗВОЗВРАТНО УДАЛИТЬ ВСЕ** свои данные:\n"
            "❌ Все кредиты и займы\n"
            "❌ Все кредитные карты\n"
            "❌ Все расходы и доходы\n"
            "❌ Все платежи\n"
            "❌ Все бюджеты\n"
            "❌ Историю банковских операций\n\n"
            "**Это действие НЕВОЗМОЖНО отменить!**\n\n"
            "Если вы уверены, напишите точно:\n"
            "`подтверждаю удаление`\n\n"
            "Для отмены напишите что-то другое.",
            parse_mode="Markdown"
        )

    async def confirm_delete_all_data(self, update: Update, context):
        """Подтверждение удаления всех данных (второй шаг)"""
        user_id = update.effective_user.id

        # Проверить что запрос был инициирован
        user_data = context.bot_data.get('user_data', {}).get(user_id, {})
        if not user_data.get('awaiting_delete_confirmation'):
            await update.message.reply_text(
                "❌ Нет активного запроса на удаление.\n"
                "Если хотите удалить все данные, сначала напишите 'удалить всё'."
            )
            return

        # Удалить все данные
        try:
            await self.db.delete_all_user_data(user_id)
            self.ai_agent.clear_history(user_id)

            # Очистить флаг ожидания
            context.bot_data['user_data'][user_id] = {}

            await update.message.reply_text(
                "✅ **Все данные удалены**\n\n"
                "База данных полностью очищена.\n"
                "Вы можете начать заново с командой /start"
            )
        except Exception as e:
            logger.error(f"Ошибка удаления данных: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Произошла ошибка при удалении данных.\n"
                "Попробуйте позже или обратитесь к администратору."
            )

    async def handle_message(self, update: Update, context):
        """Обработка всех текстовых сообщений"""
        user = update.effective_user

        # Проверка доступа
        if not self.check_access(user.id):
            await update.message.reply_text(
                f"⛔ Доступ запрещён. Ваш ID: {user.id}"
            )
            return

        message_text = update.message.text.lower().strip()

        # Проверить состояние процесса обновления остатков
        user_data = context.bot_data.get('user_data', {}).get(user.id, {})
        if user_data.get('updating_balances'):
            # Проверить на "пропустить"
            if message_text in ['пропустить', 'пропустить долг', 'skip', 'далее']:
                # Пропустить текущий долг
                debts = user_data['debts_to_update']
                current_index = user_data['current_debt_index']
                current_index += 1
                user_data['current_debt_index'] = current_index

                if current_index < len(debts):
                    next_debt = debts[current_index]
                    response = (
                        f"⏭️ Пропущено.\n\n"
                        f"**{current_index + 1}/{len(debts)}** - {next_debt['name']}\n"
                        f"Текущий остаток в системе: {next_debt['current_balance']:,.0f} руб.\n\n"
                        f"💬 Напишите **актуальный остаток долга** сейчас:"
                    )
                    await update.message.reply_text(response, parse_mode="Markdown")
                    return
                else:
                    # Все обновлены/пропущены
                    await self.db.update_debt_balance_date(user.id)
                    del context.bot_data['user_data'][user.id]
                    await update.message.reply_text(
                        "✅ Обновление завершено!\n\nСледующая проверка через 3 месяца."
                    )
                    return

            # Обработать ответ с остатком
            response = await self.handle_balance_update_response(user.id, update.message.text, context)
            if response:
                await update.message.reply_text(response, parse_mode="Markdown")
                return

        # Проверить на запрос обновления остатков
        if any(phrase in message_text for phrase in ['да, обновить остатки', 'готов обновить', 'готов', 'да обновить']):
            # Проверить не обновлялись ли уже недавно
            update_status = await self.db.get_debt_update_status(user.id)
            if update_status:
                message = await self.start_balance_update_process(user.id, context)
                await update.message.reply_text(message, parse_mode="Markdown")
                return
            else:
                # Инициализировать отслеживание
                await self.db.init_debt_balance_tracking(user.id)
                message = await self.start_balance_update_process(user.id, context)
                await update.message.reply_text(message, parse_mode="Markdown")
                return

        if message_text in ['позже', 'не сейчас', 'потом']:
            await update.message.reply_text(
                "Хорошо, напомню через неделю. Напишите **\"обновить остатки\"** когда будете готовы."
            )
            return

        # Обработка текстовых команд
        if message_text in ['начать', 'start', '/start']:
            await self.start(update, context)
            return
        elif message_text in ['помощь', 'help', '/help']:
            await self.help_command(update, context)
            return
        elif message_text in ['очистить', 'очистить историю', 'clear']:
            await self.clear_history(update, context)
            return
        elif message_text in ['удалить всё', 'удалить все данные', 'удалить все']:
            await self.request_delete_all_data(update, context)
            return
        elif message_text == 'подтверждаю удаление':
            await self.confirm_delete_all_data(update, context)
            return

        # Показать что бот печатает
        await update.message.chat.send_action(action="typing")

        # Отправить сообщение AI-агенту
        try:
            response_text, image_path = await self.ai_agent.chat(user.id, update.message.text)

            # Отправить текстовый ответ
            if response_text:
                await update.message.reply_text(response_text)

            # Отправить изображение если есть
            if image_path:
                try:
                    with open(image_path, 'rb') as photo:
                        await update.message.reply_photo(photo=photo)
                except Exception as e:
                    logger.error(f"Ошибка отправки изображения: {e}")

        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке запроса.\n"
                "Попробуйте переформулировать или напишите 'помощь'"
            )

    async def check_debt_balance_updates(self, context):
        """Периодическая проверка необходимости обновления остатков долгов"""
        logger.info("Проверка пользователей для обновления остатков долгов...")

        try:
            users_needing_update = await self.db.check_users_needing_update()

            for user in users_needing_update:
                user_id = user['user_id']
                try:
                    # Проверить есть ли у пользователя активные долги
                    loans = await self.db.get_active_loans(user_id)
                    cards = await self.db.get_active_credit_cards(user_id)

                    if not loans and not cards:
                        # Нет долгов - обновить дату без напоминания
                        await self.db.update_debt_balance_date(user_id)
                        continue

                    # Отправить напоминание
                    message = (
                        "📊 **ВРЕМЯ ОБНОВИТЬ ОСТАТКИ ДОЛГОВ**\n\n"
                        "Прошло 3 месяца с последнего обновления!\n\n"
                        "Для точного отслеживания финансов нужно обновить текущие остатки по кредитам и картам.\n\n"
                        "🔄 **Готовы обновить сейчас?**\n"
                        "Напишите: **\"Да, обновить остатки\"** или **\"Готов\"**\n\n"
                        "⏭️ Пропустить: **\"Позже\"** или **\"Не сейчас\"**"
                    )

                    await context.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode="Markdown"
                    )
                    logger.info(f"Отправлено напоминание об обновлении остатков пользователю {user_id}")

                except Exception as e:
                    logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")

        except Exception as e:
            logger.error(f"Ошибка проверки обновлений остатков: {e}")

    async def start_balance_update_process(self, user_id: int, context):
        """Запустить процесс последовательного обновления остатков"""
        # Получить все долги пользователя
        loans = await self.db.get_active_loans(user_id)
        cards = await self.db.get_active_credit_cards(user_id)

        # Создать список долгов для обновления
        debts_to_update = []

        for loan in loans:
            debts_to_update.append({
                'type': 'loan',
                'id': loan['id'],
                'name': loan['name'],
                'current_balance': loan['current_balance']
            })

        for card in cards:
            debts_to_update.append({
                'type': 'card',
                'id': card['id'],
                'name': f"Карта {card['bank_name']}",
                'current_balance': card['current_balance']
            })

        if not debts_to_update:
            return "У вас нет активных долгов для обновления."

        # Сохранить состояние в context
        if 'user_data' not in context.bot_data:
            context.bot_data['user_data'] = {}

        context.bot_data['user_data'][user_id] = {
            'updating_balances': True,
            'debts_to_update': debts_to_update,
            'current_debt_index': 0,
            'updated_count': 0
        }

        # Начать с первого долга
        first_debt = debts_to_update[0]
        message = (
            f"✅ Отлично! Давайте обновим остатки.\n\n"
            f"**1/{len(debts_to_update)}** - {first_debt['name']}\n"
            f"Текущий остаток в системе: {first_debt['current_balance']:,.0f} руб.\n\n"
            f"💬 Напишите **актуальный остаток долга** сейчас:"
        )

        return message

    async def handle_balance_update_response(self, user_id: int, message_text: str, context):
        """Обработать ответ пользователя в процессе обновления остатков"""
        user_data = context.bot_data['user_data'].get(user_id, {})

        if not user_data.get('updating_balances'):
            return None

        debts = user_data['debts_to_update']
        current_index = user_data['current_debt_index']
        current_debt = debts[current_index]

        # Попытаться распарсить сумму
        try:
            # Убрать все кроме цифр и точки/запятой
            cleaned = message_text.replace(',', '').replace(' ', '').replace('руб', '').replace('.', '')
            new_balance = float(cleaned)

            # Обновить остаток в базе
            if current_debt['type'] == 'loan':
                await self.db.update_loan(current_debt['id'], current_balance=new_balance)
            else:  # card
                await self.db.update_credit_card(current_debt['id'], current_balance=new_balance)

            user_data['updated_count'] += 1

            # Перейти к следующему долгу
            current_index += 1
            user_data['current_debt_index'] = current_index

            if current_index < len(debts):
                # Есть еще долги
                next_debt = debts[current_index]
                response = (
                    f"✅ Обновлено: {current_debt['name']} → {new_balance:,.0f} руб.\n\n"
                    f"**{current_index + 1}/{len(debts)}** - {next_debt['name']}\n"
                    f"Текущий остаток в системе: {next_debt['current_balance']:,.0f} руб.\n\n"
                    f"💬 Напишите **актуальный остаток долга** сейчас:"
                )
                return response
            else:
                # Все долги обновлены
                await self.db.update_debt_balance_date(user_id)

                # Очистить состояние
                del context.bot_data['user_data'][user_id]

                response = (
                    f"🎉 **Отлично! Все остатки обновлены!**\n\n"
                    f"Обновлено долгов: {user_data['updated_count']}\n\n"
                    f"Следующая проверка через 3 месяца.\n"
                    f"Теперь ваши данные актуальны! 💪"
                )
                return response

        except (ValueError, AttributeError) as e:
            return (
                f"❌ Не могу распознать сумму.\n\n"
                f"Попробуйте написать просто число, например:\n"
                f"• 150000\n"
                f"• 1500000\n\n"
                f"Или напишите **\"пропустить\"** чтобы оставить как есть."
            )

    async def send_daily_reminder(self, context):
        """Отправка ежедневного напоминания"""
        for user_id in ALLOWED_USER_IDS:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="⏰ Время вносить данные за день!\n\n"
                         "Просто напиши мне что потратил и получил сегодня.\n"
                         "Например:\n"
                         "• 1500 на продукты\n"
                         "• 250 за кофе\n"
                         "• 15000 на кредит в Сбере\n\n"
                         "Финансовая дисциплина - ключ к свободе! 💪"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")

    async def post_init(self, app: Application):
        """Инициализация после запуска"""
        # Инициализация базы данных
        await self.db.init_db()
        logger.info("База данных инициализирована")

        # Настройка ежедневного напоминания
        job_queue = app.job_queue
        tz = pytz.timezone(TIMEZONE)
        reminder_time = datetime_time(hour=REMINDER_HOUR, minute=REMINDER_MINUTE, tzinfo=tz)

        job_queue.run_daily(
            self.send_daily_reminder,
            time=reminder_time,
            name="daily_reminder"
        )
        logger.info(f"Ежедневное напоминание настроено на {REMINDER_HOUR}:{REMINDER_MINUTE:02d} {TIMEZONE}")

        # Настройка проверки обновлений остатков долгов (раз в день в 10:00)
        debt_check_time = datetime_time(hour=10, minute=0, tzinfo=tz)
        job_queue.run_daily(
            self.check_debt_balance_updates,
            time=debt_check_time,
            name="debt_balance_check"
        )
        logger.info(f"Проверка обновлений остатков долгов настроена на 10:00 {TIMEZONE}")

    async def error_handler(self, update: Update, context):
        """Обработка ошибок"""
        logger.error(f"Ошибка: {context.error}", exc_info=context.error)

        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Попробуйте ещё раз или напишите 'помощь'"
            )

    def run(self):
        """Запуск бота"""
        logger.info("Запуск AI финансового бота...")

        # Создание приложения
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(self.post_init).build()

        # Обработчики
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("clear", self.clear_history))

        # Основной обработчик всех текстовых сообщений
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ))

        # Обработчик ошибок
        app.add_error_handler(self.error_handler)

        # Запуск бота
        logger.info("AI бот запущен! Готов к работе 🤖")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    bot = FinanceBot()
    bot.run()
