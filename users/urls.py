from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('create/', views.user_create, name='user_create'),
    path('<int:id>/edit/', views.user_edit, name='user_edit'),
    path('<int:id>/delete/', views.user_delete, name='user_delete'),
]
