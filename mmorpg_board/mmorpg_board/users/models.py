from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.forms import Form, CharField, EmailField


# Основная форма регистрации пользователя
class UserRegisterForm(UserCreationForm):
    email = EmailField(max_length=254, label='Адрес электронной почты')
    first_name = CharField(max_length=150, required=False, label="Введите Ваше имя")

    class Meta:
        model = User
        fields = ('first_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        # При первой регистрации до подтверждения почты пользователь неактивен
        user.is_active = False
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким адресом электронной почты уже зарегистрирован в системе')
        return email


class UserEmailConfirmedForm(Form):
    random_code = CharField(max_length=6)