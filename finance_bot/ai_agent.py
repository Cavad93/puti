"""
AI-агент для разговорного управления финансами
"""
import anthropic
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import CLAUDE_API_KEY, CLAUDE_MODEL
from tools import FinancialTools


class FinancialAIAgent:
    """AI-агент на базе Claude для управления финансами"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        self.model = CLAUDE_MODEL
        self.tools = FinancialTools()

        # Хранение истории разговоров по пользователям
        self.conversations: Dict[int, List[Dict]] = {}

        # Хранение последних транзакций для возможности отмены
        self.last_transactions: Dict[int, Dict] = {}

    def _get_system_prompt(self) -> str:
        """Системный промпт для AI-агента"""
        return """Ты персональный финансовый помощник с AI. Твоя задача - помогать пользователю управлять финансами через естественный диалог.

ТВОИ ВОЗМОЖНОСТИ:
1. Понимать естественный язык:
   - "35000 на кредит в Сбере" → внести платёж по кредиту Сбербанк
   - "590 за кофе" → записать расход на кофе
   - "Получил зарплату 85000" → добавить доход
   - "У меня кредит в Альфе 300к под 16%" → добавить новый кредит

2. Запоминать контекст:
   - Помнить предыдущие сообщения
   - Различать несколько кредитов в одном банке
   - Понимать на что ссылается пользователь

3. Уточнять неоднозначности:
   - Если не понятна категория → спросить
   - Если несколько подходящих кредитов → уточнить какой
   - Если не хватает данных → запросить

4. Подтверждать большие суммы:
   - Суммы > 100 000 руб всегда подтверждай
   - Остальное записывай сразу

5. Исправлять ошибки:
   - "Это ошибка, удали" → удалить последнюю запись
   - "Измени сумму" → попросить новую сумму и обновить

5.1. ДОСРОЧНОЕ ПОГАШЕНИЕ:
   - Понимай фразы: "Что если я внесу 50000 досрочно на кредит в Сбере?"
   - Используй calculate_early_payment чтобы показать выгоду
   - Показывай экономию денег и времени

5.2. КРЕДИТНЫЕ КАНИКУЛЫ:
   - Понимай: "Мне одобрили каникулы по кредиту в Альфе с марта по май"
   - Используй set_loan_holiday для регистрации
   - Предупреждай что проценты продолжат начисляться
   - Информируй о продлении срока кредита

6. БЮДЖЕТИРОВАНИЕ (ВАЖНО!):
   - Когда пользователь говорит "давай составим бюджет на январь 2026" - создавай категории бюджета
   - Понимай фразы типа: "60000 на ремонт машины, 30000 на еду, 20000 на развлечения"
   - Создавай отдельную категорию для каждой позиции бюджета
   - АВТОМАТИЧЕСКАЯ КАТЕГОРИЗАЦИЯ расходов:
     * "купил в магазине" / "пятёрочка" / "продукты" → категория "Продукты"
     * "сходил в кино" / "кафе" / "бар" / "ресторан" → категория "Развлечения"
     * "бензин" / "заправка" / "такси" / "метро" → категория "Транспорт"
     * "кофе" / "кофейня" / "старбакс" → категория "Кофе"
     * "одежда" / "обувь" → категория "Одежда"
     * "аптека" / "врач" / "лекарства" → категория "Здоровье"
     * "ремонт машины" / "автосервис" / "сто" → категория "Ремонт машины"
     * "жкх" / "коммунальные" / "электричество" → категория "Коммунальные"
     * "телефон" / "интернет" / "связь" → категория "Связь"
   - Когда вносишь расход - система автоматически отследит бюджет
   - Если расход превысил бюджет - пользователь увидит предупреждение
   - ЗАПЛАНИРОВАННЫЕ РАСХОДЫ: понимай фразы "через 5 месяцев вернуть долг Стасу", "23.02.2026 подарок сестре 10000"

7. ОБЩИЙ БЮДЖЕТ для 2 пользователей:
   - Бюджет общий, но система отслеживает кто сколько потратил
   - Оба пользователя могут вносить расходы
   - При запросе можно показать расходы каждого отдельно

8. ИНТЕГРАЦИЯ С Т-БАНКОМ (НОВОЕ!):
   - Понимай фразы: "Подключи мою карту Т-Банка", "Добавь API токен ..."
   - Используй connect_bank_api для подключения (токен от пользователя)
   - Синхронизация: "Загрузи операции из банка", "Синхронизируй за последнюю неделю"
   - Автоматическая классификация: система сама определяет тип операции
   - ВСЕГДА уточняй верно ли понял операцию: "Я понял что это продукты, верно?"
   - Для ПЕРЕВОДОВ физлицам ОБЯЗАТЕЛЬНО спрашивай цель: "Это перевод Ивану. На что?"
   - ИГНОРИРУЙ переводы между пользователями бота (внутренние)
   - После синхронизации показывай операции и проси подтверждения

9. РЕДАКТИРОВАНИЕ ДАННЫХ (ВАЖНО!):
   - ИЗМЕНЕНИЕ КРЕДИТОВ: понимай фразы как "Нет, это текущий остаток 1455000", "Измени сумму в Почта Банке на 1455000", "Обнови ставку по кредиту в Сбере на 16%"
   - Используй update_loan для изменения параметров кредита (остаток долга, ставка, платеж, день платежа)
   - ИЗМЕНЕНИЕ КАРТ: "Долг по карте Сбера теперь 200000", "Обнови лимит на карте Тинькофф"
   - Используй update_credit_card для изменения параметров карты
   - УДАЛЕНИЕ: "Удали кредит в Почта Банке", "Убери карту Уралсиб"
   - Используй delete_loan или delete_credit_card для удаления
   - ДУБЛИКАТЫ: понимай фразы "У меня дублируется запись по Почта Банку, удали 3 записи и оставь 1"
   - Используй remove_duplicate_loans для автоматического удаления дубликатов
   - ВАЖНО: при слове "остаток", "осталось", "текущий долг" - это current_balance, НЕ principal_amount!
   - Всегда подтверждай что именно изменилось после обновления

ПРАВИЛА:
- Будь дружелюбным и понятным
- Отвечай кратко, но информативно
- Используй эмодзи для наглядности (💰 💳 📊 ✅ ❌ ⚠️)
- После каждого действия подтверждай что сделано
- Если нужна дополнительная информация - спрашивай
- Помни: у пользователя долги, твоя цель помочь выбраться
- При внесении расхода автоматически проверяется бюджет

ТЕКУЩАЯ ДАТА: {current_date}

Используй инструменты (tools) для выполнения операций. Не придумывай данные - только то, что сказал пользователь.""".format(
            current_date=datetime.now().strftime('%Y-%m-%d')
        )

    async def chat(self, user_id: int, message: str) -> tuple[str, Optional[str]]:
        """
        Обработать сообщение пользователя

        Returns:
            tuple(text_response, image_path)
        """
        # Инициализация истории для нового пользователя
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        # Добавить сообщение пользователя в историю
        self.conversations[user_id].append({
            "role": "user",
            "content": message
        })

        # Ограничить историю последними 20 сообщениями
        if len(self.conversations[user_id]) > 20:
            self.conversations[user_id] = self.conversations[user_id][-20:]

        try:
            # Вызов Claude с Tool Use
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self._get_system_prompt(),
                tools=self.tools.get_tools_definition(),
                messages=self.conversations[user_id]
            )

            # Инициализация переменных для ответа
            text_response = ""
            image_path = None

            # Обработка tool_use в цикле (может быть несколько раундов)
            current_response = response

            while True:
                # Собрать tool_use блоки из текущего ответа
                current_tool_uses = []
                current_assistant_content = []

                for block in current_response.content:
                    if block.type == "text":
                        if block.text:  # Добавить только непустой текст
                            text_response += block.text
                            current_assistant_content.append({"type": "text", "text": block.text})
                    elif block.type == "tool_use":
                        current_tool_uses.append(block)
                        current_assistant_content.append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })

                # Если есть tool_use - обработать
                if current_tool_uses:
                    # Добавить assistant message
                    self.conversations[user_id].append({
                        "role": "assistant",
                        "content": current_assistant_content
                    })

                    # Выполнить все инструменты
                    tool_results_content = []
                    for tool_block in current_tool_uses:
                        tool_name = tool_block.name
                        tool_input = tool_block.input
                        tool_use_id = tool_block.id

                        # Выполнить инструмент
                        tool_result = await self.tools.execute_tool(tool_name, tool_input, user_id)

                        # Сохранить последнюю транзакцию
                        if tool_name in ["add_income", "add_expense", "add_loan_payment"]:
                            self.last_transactions[user_id] = {
                                "tool": tool_name,
                                "input": tool_input,
                                "result": tool_result
                            }

                        # Проверить наличие изображения
                        if isinstance(tool_result, dict) and tool_result.get('image_path'):
                            image_path = tool_result['image_path']

                        # Добавить результат
                        tool_results_content.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": str(tool_result)
                        })

                    # Добавить все tool_result
                    self.conversations[user_id].append({
                        "role": "user",
                        "content": tool_results_content
                    })

                    # Получить следующий ответ
                    current_response = self.client.messages.create(
                        model=self.model,
                        max_tokens=2048,
                        system=self._get_system_prompt(),
                        tools=self.tools.get_tools_definition(),
                        messages=self.conversations[user_id]
                    )
                    # Цикл продолжится для обработки нового ответа

                else:
                    # Нет больше tool_use - сохранить финальный ответ и выйти
                    if current_assistant_content:  # Только если есть контент
                        self.conversations[user_id].append({
                            "role": "assistant",
                            "content": current_response.content
                        })
                    break

            return text_response, image_path

        except Exception as e:
            error_msg = f"❌ Произошла ошибка: {str(e)}"
            return error_msg, None

    def clear_history(self, user_id: int):
        """Очистить историю разговора"""
        if user_id in self.conversations:
            self.conversations[user_id] = []

    def get_conversation_summary(self, user_id: int) -> str:
        """Получить краткую сводку разговора"""
        if user_id not in self.conversations:
            return "История пуста"

        messages = self.conversations[user_id]
        return f"Сообщений в истории: {len(messages)}"
