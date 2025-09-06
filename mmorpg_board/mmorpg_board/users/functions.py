from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from random import randint


# Отправка кода для подтверждения почты
def send_code(email: str):
    code = randint(100000, 999999)
    cache.set(email, code, timeout=180)
    subject = 'Код для подтверждения почты'
    message = (f'Для активации почты введите в форме подтверждения почты '
               f'портала доски объявлений следующий код:\n'
               f'{code}')
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])