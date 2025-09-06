from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import CharField, Form, EmailField, PasswordInput
from django.core.cache import cache


class ConfirmEmailForm(Form):
    code = CharField(min_length=6, max_length=6)

    def __init__(self, *args, **kwargs):
        self.email = kwargs.pop('email', None)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data['code']
        cache_code = cache.get(self.email)
        if cache_code is None:
            raise ValidationError('Код подтверждения истек или не был отправлен')
        if str(code) != str(cache_code):
            raise ValidationError('Вы ввели неверный код')
        return code


class CustomAuthenticationForm(AuthenticationForm):
    username = EmailField(
        max_length=254,
        label='Адрес электронной почты',
        error_messages={
            'invalid': 'Введите корректный email адрес',
            'required': 'Email обязателен для заполнения'
        }
    )
    password = CharField(
        max_length=128,
        label='Пароль',
        widget=PasswordInput(attrs={'autocomplete': 'current-password'}),
        error_messages={
            'required': 'Пароль обязателен для заполнения'
        }
    )