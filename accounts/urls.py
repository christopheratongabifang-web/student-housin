from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.register_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
]
