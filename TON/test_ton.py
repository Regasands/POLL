import requests

from CONFIG.config import TonWallet
def create_payment(amount, currency, description, success_url, webhook_url):
    headers = {
    "Authorization": f"Token {TonWallet.ADDRESS}",
    "Content-Type": "application/json",
    }
    data = {
        "amount": amount,
        "currency": currency,
        "order_id": "unique_order_id_123",  # Уникальный ID заказа
        "description": description,
        "success_url": success_url,
        "webhook_url": webhook_url,
    }
    
    response = requests.post(BASE_URL, json=data, headers=headers)
    return response.json()

payment_info = create_payment(
    amount=100.0,  # Сумма платежа
    currency="RUB",  # Валюта
    description="Оплата товара №123",
    success_url="https://example.com/success",  # URL для успешной оплаты
    webhook_url="https://example.com/webhook",  # URL для уведомлений
)
print(payment_info)