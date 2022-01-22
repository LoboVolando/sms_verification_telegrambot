from telethon.sync import TelegramClient
from telethon import events, Button
from telethon.events import NewMessage
from decouple import config
from loguru import logger
from handler import handler

api_id = config('API_ID')
api_hash = config('API_HASH')
token = config('TOKEN')

bot = TelegramClient('bot', api_id=api_id, api_hash=api_hash).start(bot_token=token)

logger.add('logs.log', format="{time} {level} {message}", rotation='1 hour')


@logger.catch
@bot.on(events.NewMessage())
async def start(event: NewMessage.Event) -> None:
    """
    Фунция обмена сообщениями с пользователем. Отправляет в чат текст и опционально клавиатурные кнопки.
    :param event: Принимает объект NewMessage.Event
    :return: Возвращает None
    """
    logger.info(f'{event.chat_id}, {event.text}')
    keyboard = [
        [
            Button.text('Save session', resize=True),
            Button.text('Show all sessions', resize=True)
        ]
    ]

    message = event.text
    result, flag = handler(event.chat_id, message)

    if flag:
        await bot.send_message(event.chat_id, result, buttons=keyboard)
    else:
        await bot.send_message(event.chat_id, result, buttons=Button.clear())


if __name__ == "__main__":
    with bot:
        bot.run_until_disconnected()
