from django.urls import path

from apps.telegram import views

urlpatterns = [
    path('link-telegram/confirm/', views.LinkTelegramConfirmView.as_view(), name='telegram_link_confirm'),
    path('link-telegram/<str:token>/', views.LinkTelegramView.as_view(), name='telegram_link'),
]
