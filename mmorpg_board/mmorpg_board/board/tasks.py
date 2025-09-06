from celery import shared_task

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from datetime import timedelta, datetime

from .models import Subscriber, Board  # Исправлено: было Ad, должно быть Board


@shared_task
def weekly_mailing():
    # Получаем всех подписчиков
    '''Такой запрос работает с PostreSQL'''
    # subscribers = (Subscriber.objects.select_related('user').
    #                filter(categories__len__gt=0).all())

    ''' Если SQLite, то возвращаем всех подписчиков, затем "механически" фильтруем '''
    subscribers = Subscriber.objects.select_related('user').all()

    # Фильтруем, у кого есть хотя бы одна категория подписки
    subscribers = [i for i in subscribers if len(i.categories)>0]
    week_ago = datetime.now() - timedelta(days=7)

    for subscriber in subscribers:
        user = subscriber.user
        categories = subscriber.categories

        # Получаем новые объявления за неделю в категориях подписчика
        new_ads = (Board.objects.filter(
            category__in=categories,
            created_at__gte=week_ago,
        ).exclude(author_id=user.id).  # свои объявления исключаем
                   order_by('-created_at')).all()
        if not new_ads:
            continue  # Если нет новых объявлений, пропускаем пользователя

        # Генерируем HTML-письмо с помощью шаблона
        context = {
            'user': user,
            'ads': new_ads,
            'site_url': settings.SITE_URL,  # Добавлено для работы ссылок в email
        }
        email_body = render_to_string('board/partials/msg.html', context)

        # Отправляем письмо
        email = EmailMessage(
            subject=f'Еженедельная подборка объявлений в ваших категориях',
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.content_subtype = 'html'  # Разрешаем HTML
        email.send()