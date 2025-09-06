from django.urls import reverse
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.core.exceptions import ObjectDoesNotExist

from .forms import ConfirmEmailForm, CustomAuthenticationForm
from .models import UserRegisterForm
from .functions import send_code


# Представление для регистрации пользователя
class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'sign/signup.html'

    def form_valid(self, form):
        user = form.save(commit=True)
        send_code(user.email)
        return redirect('confirm_email', email=user.email)


# Переопределение класса авторизации пользователя
class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'sign/login.html'

    def form_invalid(self, form):
        email = form.data.get('username')

        if email and User.objects.filter(username=email).exists():
            try:
                user = User.objects.get(username=email)
                if not user.is_active:
                    send_code(email)
                    return redirect('confirm_email', email=email)
            except ObjectDoesNotExist:
                pass

        return super().form_invalid(form)


# Отображение формы для подтверждения почты
def confirm_email_view(request, email):
    form = ConfirmEmailForm(email=email)

    if request.method == 'POST':
        form = ConfirmEmailForm(request.POST, email=email)
        if form.is_valid():
            try:
                user = User.objects.get(email=email)
                user.is_active = True
                user.save()

                # Автоматически аутентифицируем пользователя после подтверждения email
                authenticated_user = authenticate(
                    request,
                    username=user.username,
                    password=request.POST.get('password', '')
                )
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    return redirect('ad_list')  # Перенаправляем на главную страницу
                else:
                    return redirect('login')

            except ObjectDoesNotExist:
                return redirect('signup')

    return render(request, 'sign/confirm_email.html', {'form': form, 'email': email})