from django.contrib.auth import login
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import CustomUserCreationForm
from users.models import CustomUser


class UserRegisterView(CreateView):
    model = CustomUser
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def send_welcome_email(self, user_email):
        subject = 'Добро пожаловать на сайт SkyShop!'
        message = 'Вы авторизовались.'
        from_email = 'jul1e77@yandex.ru'
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)
