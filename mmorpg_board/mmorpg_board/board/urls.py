from django.urls import path
from . import views

urlpatterns = [
    # Панель пользователя и менеджера
    path('manager/add/', views.add_manager_view, name='add_manager'),
    path('manager/send_news/', views.send_news_view, name='send_news'),
    path("subscription/", views.subscribe_form_view, name="subscribe_form"),

    # Объявления
    path("", views.AdListView.as_view(), name="ad_list"),
    path("ad/create/", views.AdCreateView.as_view(), name="ad_create"),
    path("ad/<int:pk>/", views.AdDetailView.as_view(), name="ad_detail"),
    path("ad/<int:pk>/edit/", views.AdUpdateView.as_view(), name="ad_edit"),

    # Отклики
    path("ad/<int:ad_id>/response/", views.ResponseCreateView.as_view(), name="response_create"),
    path("responses/", views.ResponseListView.as_view(), name="responses"),
    path("response/<int:pk>/accept/", views.ResponseUpdateView.as_view(), name="response_accept"),
    path("response/<int:pk>/delete/", views.ResponseDeleteView.as_view(), name="response_delete"),

    # URL для тестирования
    path("test/", views.test_view, name='test'),
]