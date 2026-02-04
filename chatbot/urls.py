from django.urls import path
from . import views

urlpatterns = [
    # ---------- AUTH ----------
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # ---------- HOME ----------
    path('', views.home, name='home'),

    # ---------- API ----------
    path('chat/', views.chat_view, name='chat'),
    path('complaint/register/', views.register_complaint),
    path('document/upload/', views.upload_document),
]
