from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('search/', views.property_search_view, name='property_search'),
    path('property/<int:pk>/', views.property_detail_view, name='property_detail'),
    path('property/<int:property_id>/inquiry/', views.submit_inquiry_view, name='submit_inquiry'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/property/add/', views.property_create_view, name='property_create'),
    path('dashboard/property/<int:pk>/edit/', views.property_edit_view, name='property_edit'),
    path('dashboard/property/<int:pk>/delete/', views.property_delete_view, name='property_delete'),
    path('chat/<int:inquiry_id>/', views.chat_view, name='chat'),
    path('chat/<int:inquiry_id>/send/', views.send_message_view, name='send_message'),
    path('dashboard/manage/landlords/', views.manage_landlords_view, name='manage_landlords'),
    path('dashboard/manage/landlords/add/', views.add_landlord_view, name='add_landlord'),
    path('dashboard/manage/landlords/<int:landlord_id>/delete/', views.delete_landlord_view, name='delete_landlord'),
]
