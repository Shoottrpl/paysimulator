import asyncio

from aiohttp import ClientSession

from app.logger import LOGS
from app.signature.signature_service import TransactionSignatureService


async def send_webhook():
    data = {
        "transaction_id": "5eae174f-7cd0-472c-bd36-35660f001123",
        "user_id": 1,
        "account_id": 2,
        "amount": 100,
    }
    url = "http://localhost:8000/api/webhook/transaction"

    generated_signature = TransactionSignatureService.generate_signature(data)
    data["signature"] = generated_signature

    async with ClientSession() as session:
        async with session.post(url, json=data) as response:
            response_data = await response.json()

        if response.status != 200:
            LOGS.error(f"Ошибка: {response.status}, {response_data}")
        else:
            LOGS.info(f"Успешно: {response_data}")


if __name__ == "__main__":
    asyncio.run(send_webhook())
