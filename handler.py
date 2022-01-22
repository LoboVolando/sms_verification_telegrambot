from loguru import logger
from random import randint
from sms import send_code
import re
import os

from datetime import datetime
from typing import Tuple

session = {}


@logger.catch()
def check_phone_valid(number: str) -> str:
    """
    Функция проверки валидности мобильного номера.
    :param number: str Принимает мобильный номер ввиде строки. Валидными считаются десятизначные номера вида
    "+79999999999" или "79999999999", начинающиеся с 79.
    :return: str Возвращает десятизначный номер без "+" или пустую строку.
    """
    result = re.findall(r'[7][9][\d]{9}', number)
    logger.info(result)
    return result[0]


@logger.catch()
def step_one(user: int, number: str) -> str:
    """
    Первый шаг диалога с пользователем. Происходит проверка номера телефона, генерация проверочного кода, отправка кода.
    Если номер телефона некорректен или отправка смс неудачна, пользователь остается на этом шаге
    :param user: int Принимает id пользователя.
    :param number: str Принимает номер телефона пользователя.
    :return: str Возвращает сообщение доя пользователя.
    """
    number = check_phone_valid(number)

    if number:
        code = randint(1000, 9999)
        logger.info(code)
        result = send_code(number, code)

        if result:
            session[user]['number'] = number
            session[user]['code'] = code
            logger.info(session)
            return f'The code has been sent to your number ***{str(number)[-4:]}'

        else:
            return "Something's wrong with your phone. Try another one"

    else:
        return 'Incorrect number. Try again'


@logger.catch()
def step_two(user: int, code: str):
    """
    Второй шаг. Проверка кода и авторизация пользователя.
    :param user: int Принимает id пользователя.
    :param code: str Принимает проверочный код, введенный пользователем.
    :return: Tuple[str, bool] Возвращает сообщение дпя пользователя и флаг отправки клавиатурных кнопок.
    """
    if str(code) == str(session[user]['code']):
        logger.info(session[user]['code'])
        logger.info(code)

        session[user]['logged'] = True
        logger.info(session)
        return "Authorization's successful! Now you can use the buttons below", True

    else:
        return 'Wrong code. Try again', False


@logger.catch()
def handler(user_id: int, message: str) -> Tuple[str, bool]:
    """
    Функция логики бота. Ведет пользователя по воронке диалога. По ходу диалога проверяет, какие данные пользователя
    записаны в сессию диалога. Записывает данные в файл сессии. Возвращает "список" всех сессий.
    :param user_id: int Принимает id пользователя.
    :param message: str Принимает сообщение пользователя.
    :return: Tuple[str, bool] Возвращает сообщение дпя пользователя и флаг отправки клавиатурных кнопок.
    """
    if user_id in session:

        if 'logged' in session[user_id]:

            if message == 'Save session':
                logger.info(session)

                with open(f'{session[user_id]["number"]}.session', 'a', encoding='utf8') as session_file:
                    session_file.write(f'{datetime.now()} - id: {user_id}, phone: {session[user_id]["number"]}')
                return 'Session saved', True

            elif message == 'Show all sessions':
                result = '\n'.join(name for name in os.listdir('.') if name.endswith('session')
                                   and not name.startswith('bot'))
                logger.info(result)

                if result:
                    return result, True
                else:
                    return 'No sessions yet saved', True

            return 'Choose action. Buttons below', True

        elif 'code' in session[user_id]:
            return step_two(user_id, message)
        else:
            return step_one(user_id, message), False

    else:
        session[user_id] = dict()
        return "You need to authenticate. Please provide your phone number (e.g. 79999876534). We'll send you a code", \
               False
