from django.contrib import admin
from .models import Board, Response, Subscriber, Manager


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content')


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('ad', 'author', 'created_at', 'is_accepted')
    list_filter = ('is_accepted', 'created_at')


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('user', 'categories')


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('manager',)