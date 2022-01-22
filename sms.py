import vonage
from decouple import config
from loguru import logger


@logger.catch
def send_code(phone_number: str, code: int) -> bool:
    """
    Функция отправки смс с проверочным кодом для авторизации.
    :param phone_number: str Принимает десятизначный российский мобильный номер в виде строки.
    :param code: int Принимает четырехзначный проверочный код.
    :return: bool Возвращает True в случае удпчной отправки смс и False в противном случае
    """
    key = config('VONAGE_KEY')
    secret = config('VONAGE_SECRET')

    client = vonage.Client(key=key, secret=secret)
    sms = vonage.Sms(client)

    response_data = sms.send_message(
        {
            "from": "Vonage APIs",
            "to": phone_number,
            "text": code,
        }
    )

    if response_data["messages"][0]["status"] == "0":
        print("Message sent successfully.")
        return True

    else:
        print(f"Message failed with error: {response_data['messages'][0]['error-text']}")
        return False
