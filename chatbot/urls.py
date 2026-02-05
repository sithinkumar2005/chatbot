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
    path('document/upload/', views.upload_document),

    # ---------- complaint ----------
    path("complaint/", views.complaint_page),
    path("complaint/register/", views.register_complaint),
    path("complaint/status/<str:cid>/", views.complaint_status),
]
