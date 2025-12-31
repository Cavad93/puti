"""
Интеграция с API Т-Банка (Tinkoff)
"""
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TBankAPI:
    """Клиент для работы с API Т-Банка"""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://business.tbank.ru/openapi/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    async def get_statement(
        self,
        from_date: str,
        to_date: str,
        limit: int = 1000,
        cursor: Optional[str] = None
    ) -> Dict:
        """
        Получить выписку по операциям

        Args:
            from_date: Дата начала периода (ISO 8601, UTC)
            to_date: Дата окончания периода (ISO 8601, UTC)
            limit: Количество операций (макс 5000, по умолчанию 1000)
            cursor: Курсор для пагинации

        Returns:
            Словарь с операциями и курсором для следующей страницы
        """
        url = f"{self.base_url}/statement"

        params = {
            "from": from_date,
            "to": to_date,
            "limit": limit
        }

        if cursor:
            params["cursor"] = cursor

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "operations": data.get("operations", []),
                            "nextCursor": data.get("nextCursor")
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"T-Bank API error {response.status}: {error_text}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "details": error_text
                        }
        except Exception as e:
            logger.error(f"T-Bank API request failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def sync_recent_operations(self, days: int = 7) -> List[Dict]:
        """
        Синхронизировать операции за последние N дней

        Args:
            days: Количество дней для синхронизации

        Returns:
            Список всех операций
        """
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=days)

        from_str = from_date.isoformat() + "Z"
        to_str = to_date.isoformat() + "Z"

        all_operations = []
        cursor = None

        while True:
            result = await self.get_statement(from_str, to_str, cursor=cursor)

            if not result["success"]:
                logger.error(f"Failed to sync operations: {result.get('error')}")
                break

            operations = result.get("operations", [])
            all_operations.extend(operations)

            cursor = result.get("nextCursor")
            if not cursor:
                break

        return all_operations

    def parse_operation(self, operation: Dict) -> Dict:
        """
        Парсинг операции из формата T-Bank в наш формат

        Args:
            operation: Операция из API T-Bank

        Returns:
            Словарь с нормализованными данными
        """
        # Определение типа операции
        operation_type = operation.get("type", "")
        amount = float(operation.get("amount", 0))

        # Классификация операции
        if amount > 0:
            op_category = "income"
        elif amount < 0:
            op_category = "expense"
        else:
            op_category = "unknown"

        # Извлечение данных о контрагенте
        counterparty = operation.get("counterparty", {})

        return {
            "operation_id": operation.get("id") or operation.get("operationId"),
            "operation_date": operation.get("date") or operation.get("operationDate"),
            "amount": abs(amount),
            "currency": operation.get("currency", "RUB"),
            "operation_type": op_category,
            "description": operation.get("description") or operation.get("purpose", ""),
            "category": operation.get("category"),
            "mcc_code": operation.get("mcc"),
            "counterparty_name": counterparty.get("name"),
            "counterparty_account": counterparty.get("account"),
            "raw_type": operation_type
        }

    def classify_operation(self, operation: Dict) -> str:
        """
        Классификация операции для AI

        Args:
            operation: Операция

        Returns:
            Строка с предварительной классификацией
        """
        desc = operation.get("description", "").lower()
        mcc = operation.get("mcc_code", "")

        # MCC коды для категоризации
        mcc_categories = {
            "5411": "Продукты",  # Супермаркеты
            "5812": "Развлечения",  # Кафе/рестораны
            "5541": "Транспорт",  # Заправки
            "4121": "Транспорт",  # Такси
            "5912": "Здоровье",  # Аптеки
        }

        if mcc in mcc_categories:
            return mcc_categories[mcc]

        # Классификация по описанию
        if any(word in desc for word in ["магазин", "супермаркет", "пятёрочка", "лента"]):
            return "Продукты"
        elif any(word in desc for word in ["кафе", "ресторан", "кино", "бар"]):
            return "Развлечения"
        elif any(word in desc for word in ["бензин", "заправка", "азс", "такси"]):
            return "Транспорт"
        elif any(word in desc for word in ["аптека", "медицина", "врач"]):
            return "Здоровье"

        return "Другое"
