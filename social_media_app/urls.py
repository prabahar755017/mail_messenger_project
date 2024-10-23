from django.urls import path
from . import views  # or from your_app.views import your_view

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-password-reset/', views.verify_password_reset, name='verify_password_reset'),
    path('reset-password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
     path('send-message/',views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('sent_messages/',  views.sent_messages, name='sent_messages'),  # New URL for sent messages
    path('delete-message/<int:message_id>/',  views.delete_message, name='delete_message'),
    path('', views.index, name='index'),
]